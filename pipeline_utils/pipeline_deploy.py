#!/usr/bin/env python3

################################################
#
#   pipeline_deploy, from YAML format
#
#   Michele Berselli - berselli.michele@gmail.com
#
################################################

import os, sys, subprocess
import shutil
import json
import glob
import boto3
import structlog
import hashlib
from dcicutils import ff_utils, s3_utils
from dcicutils.codebuild_utils import CodeBuildUtils
from pipeline_utils.lib import yaml_parser


###############################################################
#   REPOSITORY
#
### Expected structure for the pipeline repository
#
#   pipeline
#       descriptions
#       dockerfiles
#            <image>
#                Dockerfile
#       portal_objects
#           workflows
#               <workflow>.yaml
#           metaworkflows
#               <metaworkflow>.yaml
#           file_format.yaml
#           file_reference.yaml
#           software.yaml
#       PIPELINE
#       VERSION
#
###############################################################


###############################################################
#   Logger
###############################################################
logger = structlog.getLogger(__name__)


###############################################################
#   PostPatchRepo, class definition
###############################################################
class PostPatchRepo(object):
    """Class to handle deployment of pipeline components.
    """

    def __init__(self, args, repo, version_file='VERSION', pipeline_file='PIPELINE', version=None):
        """Constructor method.

            :param args: Command line arguments
            :type args: object returned by ArgumentParser.parse_args() method
            :param repo: Name of the repository
            :type repo: str
            :param version_file: Name of the file storing pipeline version information
            :type version_file: str
            :param pipeline_file: Name of the file storing pipeline name information
            :type pipeline_file: str
            :param version: Pipeline version to use
            :type version: str
        """
        # Init attributes
        self.ff_key = None
        self.kms_key_id = None
        self.repo = repo
        self.object_ = {
            'Software': yaml_parser.YAMLSoftware,
            'FileFormat': yaml_parser.YAMLFileFormat,
            'ReferenceFile': yaml_parser.YAMLReferenceFile,
            'ReferenceGenome': yaml_parser.YAMLReferenceGenome,
            'Workflow': yaml_parser.YAMLWorkflow,
            'MetaWorkflow': yaml_parser.YAMLMetaWorkflow
        }
        self.filepath = {
            # .yaml files
            'Software': 'portal_objects/software.yaml',
            'FileFormat': 'portal_objects/file_format.yaml',
            'ReferenceFile': 'portal_objects/file_reference.yaml',
            'ReferenceGenome': 'portal_objects/reference_genome.yaml',
            # .yml files
            'Software_yml': 'portal_objects/software.yml',
            'FileFormat_yml': 'portal_objects/file_format.yml',
            'ReferenceFile_yml': 'portal_objects/file_reference.yml',
            'ReferenceGenome_yml': 'portal_objects/reference_genome.yml',
            # folders
            'Workflow': 'portal_objects/workflows',
            'MetaWorkflow': 'portal_objects/metaworkflows',
            'ECR': 'dockerfiles',
            'WFL': 'descriptions'
        }

        # Load attributes
        for key, val in vars(args).items():
            setattr(self, key, val)

        # Get pipeline version
        if not version:
            with open(f'{self.repo}/{version_file}') as f:
                self.version = f.readlines()[0].strip()
        else:
            self.version = version
        # Get pipeline name
        with open(f'{self.repo}/{pipeline_file}') as f:
            self.pipeline = f.readlines()[0].strip()

        # Load credentials
        self._get_credentials()
        self._codebuild = CodeBuildUtils()

    def _check_identity(self, hash, data_json):
        """Helper to check if hash is present in JSON object
        and match.

        If present, hash is stored in JSON object tags list 
        as the string 'DEPLOY_HASH-<hash_value>'.
        """
        # Get tags from JSON object
        tags = data_json.get('tags', [])

        # Get hash from tags if present
        hash_, hash_idx = None, None
        for i, tag in enumerate(tags):
            if tag.startswith('DEPLOY_HASH-'):
                hash_ = tag.split('DEPLOY_HASH-')[-1]
                hash_idx = i
                break

        # Compare hash values
        if hash_ is None:
            # object is not up to date
            # hash is not present, add hash
            tags.append(f'DEPLOY_HASH-{hash}')
            return False, tags
        # hash is present
        if hash_ == hash:
            # object is up to date
            # hash is present and values match, nothing to do
            return True, tags
        else:
            # object is not up to date
            # hash is present but differs, update hash
            tags[hash_idx] = f'DEPLOY_HASH-{hash}'
            return False, tags

    def _get_credentials(self):
        """Get auth credentials.
        """
        # Get portal credentials
        if os.path.exists(self.keydicts_json):
            with open(os.path.expanduser(self.keydicts_json)) as keyfile:
                keys = json.load(keyfile)
            self.ff_key = keys.get(self.ff_env)
        elif os.environ.get('GLOBAL_ENV_BUCKET') and os.environ.get('S3_ENCRYPT_KEY'):
            s3 = s3_utils.s3Utils(env=self.ff_env)
            self.ff_key = s3.get_access_keys('access_key_admin')
        else:
            raise Exception('Required deployment vars GLOBAL_ENV_BUCKET and/or S3_ENCRYPT_KEY not set, and no entry for specified enivornment exists in keydicts file.')

        # Get encryption key
        self.kms_key_id = os.environ.get('S3_ENCRYPT_KEY_ID', None)

    def _hash_json(self, data_json):
        """Helper to hash JSON object.
        """
        # Serialize JSON object into a consistent string
        # sort_keys=True ensures consistent key order
        # separators=(',', ':') removes unnecessary whitespace
        json_string = json.dumps(data_json, sort_keys=True, separators=(',', ':'))

        # Use a hash function to create a hash
        return hashlib.sha256(json_string.encode('utf-8')).hexdigest()

    def _post_patch_json(self, data_json, type):
        """Helper to POST|PATCH JSON object.
        """
        # Calculate the hash of the JSON object
        hash = self._hash_json(data_json)

        # Use uuid if available as unique identifier,
        #   else use the alias
        uuid = data_json.get('uuid', data_json['aliases'][0])

        if self.verbose:
            logger.info(json.dumps(data_json, sort_keys=True, indent=2))

        # Check if object already exists on the portal
        is_patch, current_json, tags = True, None, []
        try:
            # try to get the object from the portal
            current_json = ff_utils.get_metadata(uuid, add_on="frame=raw&datastore=database", key=self.ff_key)
        except Exception:
            # object does not exist, need to POST
            is_patch = False

        if is_patch:
            # object exists
            # check if object is already up to date
            is_same, tags = self._check_identity(hash, current_json)
            if is_same:
                # object is the same, nothing to do
                logger.info('> Object %s already up to date, skipping...' % data_json['aliases'][0])
                return

        # Object does not exist or changed
        #   adding or updating hash
        if not tags:
            # the object does not exist
            # add the hash to tags
            tags = [f'DEPLOY_HASH-{hash}']
        # Add or replace the updated tags to the object
        data_json['tags'] = tags

        ###########################################################
        # Exception for uploading of ReferenceFile objects
        #   status -> uploading, uploaded
        #   default is None -> the status will not be updated during patch,
        #     and set to uploading if post for the first time
        if type == 'ReferenceFile':
            # main status
            if data_json['status'] is None:
                if is_patch:
                    del data_json['status']
                else: # is first time post
                    data_json['status'] = 'uploading'

            # extra_files status
            if data_json.get('extra_files'):
                extra_files_ = []
                for ext in data_json['extra_files']:
                    ext_ = {
                        'file_format': ext,
                        'status': data_json.get('status', 'uploaded')
                    }
                    extra_files_.append(ext_)
                data_json['extra_files'] = extra_files_
        ###########################################################
        # POST|PATCH the object
        try:
            if is_patch:
                if not self.debug:
                    ff_utils.patch_metadata(data_json, uuid, key=self.ff_key)
                logger.info('> Patched %s' % data_json['aliases'][0])
            else:
                if not self.debug:
                    ff_utils.post_metadata(data_json, type, key=self.ff_key)
                logger.info('> Posted %s' % data_json['aliases'][0])
        except Exception as E:
            # this will exit and report errors during patching and posting
            logger.info('> FAILED PORTAL VALIDATION')
            logger.info(E)
            sys.exit('\nExiting...')

    def _yaml_to_json(self, data_yaml, YAMLClass, **kwargs):
        """Helper to validate YAML object and convert to JSON.
        """
        if self.validate:
            logger.info('> Validating %s' % data_yaml.get('name'))
            try:
                YAMLClass(data_yaml).to_json(**kwargs)
            except yaml_parser.ValidationError as e:
                # log errors
                for error in e.errors:
                    logger.error('- ValidationError [{0}]: {1} in path={2}, schema={3}'.format(
                                    error.validator,
                                    error.message,
                                    error.relative_path,
                                    error.schema
                                    )
                                )
        else:
            logger.info('> Processing %s' % data_yaml.get('name'))
            return YAMLClass(data_yaml).to_json(**kwargs)

        return

    def _post_patch_file(self, type):
        """
            'Software', 'FileFormat', 'ReferenceFile', 'ReferenceGenome'
        """
        logger.info(f'@ {type}...')

        # Set general variables
        filepath_ = f'{self.repo}/{self.filepath[type]}'

        # Check .yaml
        if not os.path.isfile(filepath_):

            # Check .yml
            type_yml = f'{type}_yml'
            filepath_ = f'{self.repo}/{self.filepath[type_yml]}'
            if not os.path.isfile(filepath_):
                logger.error(f'WARNING: {self.filepath[type]} or .yml not found in {self.repo}, skipping...')
                return

        # Read YAML file and create JSON objects from documents in file
        for d in yaml_parser.load_yaml(filepath_):
            # creating JSON object
            d_ = self._yaml_to_json(
                        d, self.object_[type],
                        submission_centers=self.submission_centers,
                        consortia=self.consortia
                        )
            # post/patch object
            if d_: self._post_patch_json(d_, type)

    def _post_patch_folder(self, type):
        """
            'Workflow', 'MetaWorkflow'
        """
        logger.info(f'@ {type}...')

        # Set general variables
        filepath_ = f'{self.repo}/{self.filepath[type]}'

        # Check
        if not os.path.isdir(filepath_):
            logger.error(f'WARNING: {self.filepath[type]} not found in {self.repo}, skipping...')
            return

        # Create JSON objects
        files_ = glob.glob(f'{filepath_}/*.yaml')
        files_.extend(glob.glob(f'{filepath_}/*.yml'))
        for fn in files_:
            for d in yaml_parser.load_yaml(fn):
                # creating _yaml_to_json **kwargs
                kwargs_ = {
                    'version': self.version,
                    'submission_centers': self.submission_centers,
                    'consortia': self.consortia
                }
                if type == 'Workflow':
                    kwargs_.setdefault(
                        'wflbucket_url', f's3://{self.wfl_bucket}/{self.pipeline}/{self.version}'
                    )
                # creating JSON object
                d_ = self._yaml_to_json(
                            d, self.object_[type],
                            **kwargs_
                            )
                # post/patch object
                if d_:
                    self._post_patch_json(d_, type)

    def _post_patch_wfl(self, type='WFL'):
        """
        """
        logger.info('@ Workflow Description...')

        # Set general variables
        filepath_ = f'{self.repo}/{self.filepath[type]}'
        upload_ = f'{filepath_}/upload'
        account_ = f'{self.account}.dkr.ecr.{self.region}.amazonaws.com'
        auth_keys_ = {
            'ServerSideEncryption': 'aws:kms',
            'SSEKMSKeyId': self.kms_key_id
            }

        # Check
        if not os.path.isdir(filepath_):
            logger.error(f'WARNING: {self.filepath[type]} not found in {self.repo}, skipping...')
            return

        # Create s3 object
        s3 = boto3.resource('s3')

        # Make tmp dir for upload
        if os.path.isdir(upload_):
            shutil.rmtree(upload_)
        os.mkdir(upload_)

        # Read description files and create modified files for upload
        #   placeholder variables will be replaced
        #   with specific values for the target environment
        files_ = glob.glob(f'{filepath_}/*.cwl')
        files_.extend(glob.glob(f'{filepath_}/*.wdl'))
        for fn in map(os.path.basename, files_):
            logger.info('> Processing %s' % fn)
            # set file specific variables
            file_ = f'{filepath_}/{fn}'
            upload_file_ = f'{upload_}/{fn}'
            s3_file_ = f'{self.pipeline}/{self.version}/{fn}'
            if not self.debug:
                # create modified description file for upload
                with open(file_, 'r') as read_:
                    with open(upload_file_, 'w') as write_:
                        # replace generic variables
                        for line in read_:
                            line = line.replace('ACCOUNT', account_)
                            line = line.replace('VERSION', self.version)
                            if self.sentieon_server:
                                line = line.replace('LICENSEID', self.sentieon_server)
                            write_.write(line)
                # upload to s3
                if self.kms_key_id:
                    s3.meta.client.upload_file(upload_file_, self.wfl_bucket, s3_file_, ExtraArgs=auth_keys_)
                else: # no kms_key_id, ExtraArgs not needed
                    s3.meta.client.upload_file(upload_file_, self.wfl_bucket, s3_file_)
                logger.info('> Posted %s' % s3_file_)
                # delete file to allow tmp folder to be deleted at the end
                os.remove(upload_file_)

        # Clean tmp directory
        os.rmdir(upload_)

    def _post_patch_ecr(self, type='ECR'):
        """
        """
        logger.info('@ Docker Image...')

        # Set general variables
        filepath_ = f'{self.repo}/{self.filepath[type]}'
        account_ = f'{self.account}.dkr.ecr.{self.region}.amazonaws.com'

        # Check
        if not os.path.isdir(filepath_):
            logger.error(f'WARNING: {self.filepath[type]} not found in {self.repo}, skipping...')
            return

        # Create ecr object
        ecr = boto3.client('ecr')
        response = ecr.describe_repositories()

        # Generic bash commands to be modified to correct version and account information
        for fn in map(os.path.basename, glob.glob(f'{filepath_}/*')):
            logger.info('> Processing %s' % fn)
            if not self.debug:
                # set specific variables
                tag_ = f'{account_}/{fn}:{self.version}'
                path_ = f'{filepath_}/{fn}'
                is_repository = False
                # check if tag is present in ECR repositories,
                #   if not create it
                for repository in response['repositories']:
                    if repository['repositoryArn'].split('/')[-1] == fn:
                        is_repository = True
                        break
                if not is_repository:
                    logger.info('> Creating ECR Repository %s' % fn)
                    ecr.create_repository(repositoryName=fn)
                # build and push the image
                #   do so by local build or triggering a CodeBuild run
                build_projects = self._codebuild.list_projects()
                if self.builder:
                    builder_ = self.builder
                else:
                    builder_ = f'{self.ff_env}-pipeline-builder'
                builder = list(filter(lambda b: builder_ == b, build_projects))
                if self.local_build:
                    # TODO
                    #   enable amd/arm build
                    image = f"""
                            aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {account_}
                            docker build -t {tag_} {path_} --no-cache
                            docker push {tag_}
                        """ # note that we are ALWAYS doing no-cache builds so that we can get updated base images whenever applicable
                    subprocess.check_call(image, shell=True)
                elif not builder:
                    logger.error('NOTE: no builder job found in Build projects!')
                else:
                    self._codebuild.run_project_build_with_overrides(
                        project_name=builder[0], # there should only be one
                        branch=self.branch, # this is the branch to use
                        env_overrides={
                            'IMAGE_REPO_NAME': fn,
                            'IMAGE_TAG': self.version,
                            'BUILD_PATH': path_
                        }
                    )

    def run_post_patch(self):
        """Main function to deploy specified components.
        """
        logger.info('#- %s' % self.repo)

        # Software
        if self.post_software:
            self._post_patch_file('Software')

        # FileFormat
        if self.post_file_format:
            self._post_patch_file('FileFormat')

        # ReferenceFile
        if self.post_file_reference:
            self._post_patch_file('ReferenceFile')

        # ReferenceGenome
        if self.post_reference_genome:
            self._post_patch_file('ReferenceGenome')

        # Workflow
        if self.post_workflow:
            self._post_patch_folder('Workflow')

        # Metaworkflow
        if self.post_metaworkflow:
            self._post_patch_folder('MetaWorkflow')

        # Workflow Descriptions
        if self.post_wfl:
            self._post_patch_wfl()

        # ECR
        if self.post_ecr:
            self._post_patch_ecr()


################################################
#  MAIN, runner
################################################
def main(args):
    """Deploy pipeline components from specified repositories to target environment.

    For each repository a PostPatchRepo object is created to:
        - Create and POST|PATCH to database objects in JSON format for
          Workflow, MetaWorkflow, ReferenceFile, FileFormat, and Software components
        - PUSH workflow descriptions to target S3 bucket
        - BUILD Docker images and PUSH to target ECR folder
    """

    if not args.wfl_bucket:
        if args.post_workflow or args.post_wfl:
            error = 'MISSING ARGUMENT, --post-wfl | --post-workflow requires --wfl-bucket argument.\n'
            sys.exit(error)

    if not args.account:
        if args.post_workflow or args.post_wfl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-wfl | --post-workflow | --post-ecr requires --account argument.\n'
            sys.exit(error)

    if not args.region:
        if args.post_workflow or args.post_wfl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-wfl | --post-workflow | --post-ecr requires --region argument.\n'
            sys.exit(error)

    # Get override version if flag is set
    if args.version_file:
        with open(args.version_file) as f:
            version = f.readlines()[0].strip()
    else: version = None
    # Run
    for repo in args.repos:
        pprepo = PostPatchRepo(args, repo, version=version)
        pprepo.run_post_patch()
