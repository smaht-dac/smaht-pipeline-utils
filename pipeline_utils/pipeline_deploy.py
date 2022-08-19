#!/usr/bin/env python3

################################################
#
#   pipeline_deploy, from YAML format
#
#   Michele Berselli - berselli.michele@gmail.com
#
################################################

import os, sys, subprocess
import json
import glob
import boto3
import structlog
from dcicutils import ff_utils, s3_utils
from pipeline_utils.lib import yaml_parser


###############################################################
#   REPOSITORY
#
### Expected structure for the pipeline repository
#
#   pipeline
#       wfl
#       dockerfiles
#            <image>
#                Dockerfile
#       portal_objects
#           workflows
#               <wfl>.yaml
#           metaworkflows
#               <mwfl>.yaml
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


    def __init__(self, args, repo, version='VERSION', pipeline='PIPELINE'):
        """
        """
        # Init credentials
        self.ff_key = None
        self.kms_key_id = None
        self.repo = repo
        self.object_ = {
            'Software': yaml_parser.YAMLSoftware,
            'FileFormat': yaml_parser.YAMLFileFormat,
            'FileReference': yaml_parser.YAMLFileReference,
            'Workflow': yaml_parser.YAMLWorkflow,
            'MetaWorkflow': yaml_parser.YAMLMetaWorkflow
        }
        self.filepath = {
            'Software': 'portal_objects/software.yaml',
            'FileFormat': 'portal_objects/file_format.yaml',
            'FileReference': 'portal_objects/file_reference.yaml',
            'Workflow': 'portal_objects/workflows',
            'MetaWorkflow': 'portal_objects/metaworkflows',
            'ECR': 'dockerfiles',
            'WFL': 'wfl'
        }

        # Load attributes
        for key, val in vars(args).items():
            setattr(self, key, val)

        # Get pipeline version
        with open(f'{self.repo}/{version}') as f:
            self.version = f.readlines()[0].strip()
        # Get pipeline name
        with open(f'{self.repo}/{pipeline}') as f:
            self.pipeline = f.readlines()[0].strip()

        # Load credentials
        # self._get_credentials()


    def _get_credentials(self):
        """Get auth credentials to target portal and environment.
        """
        # Get portal credentials
        if os.environ.get('GLOBAL_BUCKET_ENV') and os.environ.get('S3_ENCRYPT_KEY'):
            # new account
            s3 = s3_utils.s3Utils(env=self.ff_env)
            self.ff_key = s3.get_access_keys('access_key_admin')
        elif os.environ.get('S3_ENCRYPT_KEY'):
            # main account, also need the key to get auth this way
            self.ff_key = ff_utils.get_authentication_with_server(ff_env=self.ff_env)
        else:
            # read key for portal auth from self.keydicts_json [~/.cgap-keydicts.json]
            try:
                with open(os.path.expanduser(self.keydicts_json)) as keyfile:
                    keys = json.load(keyfile)
            except Exception:
                error = 'ERROR, could not locate file with key dicts for portal auth --keydicts-json\n'
                sys.exit(error)
            self.ff_key = keys.get(self.ff_env)

        # Get encryption key
        self.kms_key_id = os.environ.get('S3_ENCRYPT_KEY_ID', None)

        # Check args
        if not self.ff_key:
            error = 'ERROR, missing key for {0} environment in key dicts for auth\n'.format(self.ff_env)
            sys.exit(error)


    def _post_patch_json(self, data_json, type):
        """Routine to POST|PATCH metadata from JSON object to portal.
        """
        if not self.debug:
            is_patch = True
            # try:
            #     ff_utils.get_metadata(data_json['aliases'][0], key=self.ff_key)
            # except Exception:
            #     is_patch = False

            # Exception for uploading of FileReference objects
            #   status -> uploading, uploaded
            #   default is None -> the status will not be updated during patch,
            #     and set to uploading if post for the first time
            if type == 'FileReference':
                # main status
                if data_json['status'] == None:
                    if is_patch:
                        del data_json['status']
                    else: # is first time post
                        data_json['status'] = 'uploading'

                # extra_files status
                extra_files_ = []
                for ext in data_json['extra_files']:
                    ext_ = {
                        'file_format': ext,
                        'status': data_json.get('status', 'uploaded')
                    }
                    extra_files_.append(ext_)
                data_json['extra_files'] = extra_files_
            ###########################################################

            # if is_patch:
            #     ff_utils.patch_metadata(data_json, data_json['aliases'][0], key=self.ff_key)
            # else:
            #     ff_utils.post_metadata(data_json, type, key=self.ff_key)

            logger.info('> Posted %s' % data_json['aliases'][0])

        if self.verbose:
            logger.info(json.dumps(data_json, sort_keys=True, indent=2))


    def _yaml_to_json(self, data_yaml, YAMLClass, **kwargs):
        """Routine to validate YAML object and convert to JSON.
        """
        if self.validate:
            logger.info('> Validating %s' % data_yaml.get('name'))
            try:
                YAMLClass(data_yaml).to_json(**kwargs)
            except yaml_parser.SchemaError:
                pass
        else:
            logger.info('> Processing %s' % data_yaml.get('name'))
            return YAMLClass(data_yaml).to_json(**kwargs)

        return


    def _post_patch_file(self, type):
        """
            'Software', 'FileFormat', 'FileReference'
        """
        logger.info(f'@ {type}...')

        # Set general variables
        filepath_ = f'{self.repo}/{self.filepath[type]}'

        # Check
        if not os.path.isfile(filepath_):
            logger.error(f'WARNING: {self.filepath[type]} not found in {self.repo}, skipping...')
            return

        # Read YAML file and create JSON objects from documents in file
        for d in yaml_parser.load_yaml(filepath_):
            # creating JSON object
            d_ = self._yaml_to_json(
                        d, self.object_[type],
                        INSTITUTION=self.institution,
                        PROJECT=self.project
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
        for fn in glob.glob(f'{filepath_}/*.yaml'):
            for d in yaml_parser.load_yaml(fn):
                # creating _yaml_to_json **kwargs
                kwargs_ = {
                    'VERSION': self.version,
                    'INSTITUTION': self.institution,
                    'PROJECT': self.project
                }
                if type == 'Workflow':
                    kwargs_.setdefault(
                        'WFLBUCKET_URL', f's3://{self.wfl_bucket}/{self.pipeline}/{self.version}'
                    )
                # creating JSON object
                d_ = self._yaml_to_json(
                            d, self.object_[type],
                            **kwargs_
                            )
                # post/patch object
                if d_: self._post_patch_json(d_, type)


    def _post_patch_wfl(self, type='WFL'):
        """
        """
        logger.info('@ Workflow Description...')

        # Set general variables
        filepath_ = f'{self.repo}/{self.filepath[type]}'
        upload_ = f'{filepath_}/upload'
        account_ = f'{self.account}.dkr.ecr.{self.region}.amazonaws.com'
        update_ = {
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
        os.mkdir(upload_)

        # Read description files and create modified files for upload
        #   placeholder variables will be replaced
        #   with specific values for the target environment
        files_ = glob.glob(f'{filepath_}/*.cwl')
        files_.extend(glob.glob(f'{filepath_}/*.wdl'))
        for fn in files_:
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
                            line = line.replace('LICENSEID', self.sentieon_server)
                            write_.write(line)
                # upload to s3
                extra_args = {'ACL': 'public-read'}  # note that this is no longer public if using encryption!
                if self.kms_key_id:
                    extra_args.update(update_)
                s3.meta.client.upload_file(upload_file_, self.wfl_bucket, s3_file_, ExtraArgs=extra_args)
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

        # Generic bash commands to be modified to correct version and account information
        for fn in glob.glob(f'{filepath_}/*'):
            logger.info('> Processing %s' % fn)
            if not self.debug:
                # set specific variables
                tag_ = f'{account_}/{fn}:{self.version}'
                path_ = f'{filepath_}/{fn}'
                image = f"""
                            aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {account_}
                            docker build -t {tag_} {path_} --no-cache
                            docker push {tag_}
                        """ # note that we are ALWAYS doing no-cache builds so that we can get updated base images whenever applicable
                subprocess.check_call(cmd, shell=True)


    def run_post_patch(self):
        """Main function to deploy and POST|PATCH specified objects.
        """
        # Software
        if self.post_software:
            self._post_patch_file('Software')

        # FileFormat
        if self.post_file_format:
            self._post_patch_file('FileFormat')

        # FileReference
        if self.post_file_reference:
            self._post_patch_file('FileReference')

        # Workflow
        if self.post_workflow:
            self._post_patch_folder('Workflow')

        # Metaworkflow
        if self.post_metaworkflow:
            self._post_patch_folder('MetaWorkflow')

        # Wfl
        if self.post_wfl:
            self._post_patch_wfl()

        # ECR
        if self.post_ecr:
            self._post_patch_ecr()


################################################
#  MAIN, runner
################################################
def main(args):
    """Deploy pipelines from specified repositories.

    For each repository to deploy use a PostPatchRepo object to:
        - POST|PATCH portal objects
        - PUSH workflow descriptions to target environment
        - BUILD Docker images and PUSH to target environment
    """

    if not args.wfl_bucket:
        if args.post_workflow or args.post_wfl:
            error = 'MISSING ARGUMENT, --post-wfl | --post-workflow requires --wfl-bucket argument\n'
            sys.exit(error)

    if not args.account:
        if args.post_workflow or args.post_wfl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-wfl | --post-workflow | --post-ecr requires --account argument\n'
            sys.exit(error)

    if not args.region:
        if args.post_workflow or args.post_wfl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-wfl | --post-workflow | --post-ecr requires --region argument\n'
            sys.exit(error)

    if not args.project:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --project argument\n'
            sys.exit(error)

    if not args.institution:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --institution argument\n'
            sys.exit(error)

    # Run
    for repo in args.repos:
        pprepo = PostPatchRepo(args, repo)
        pprepo.run_post_patch()
