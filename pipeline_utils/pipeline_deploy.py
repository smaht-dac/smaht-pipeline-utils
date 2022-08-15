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
#   Logger
###############################################################
logger = structlog.getLogger(__name__)


###############################################################
#   Functions
###############################################################
###############################################################
#   _post_patch_routine
###############################################################
def _post_patch_routine(data_json, type, ff_key, verbose=False, debug=False):
    """
    """
    if not debug:
        is_patch = True
        # try:
        #     ff_utils.get_metadata(data_json['aliases'][0], key=ff_key)
        # except Exception:
        #     is_patch = False

        # Exception for uploading of File Reference objects
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
        #     ff_utils.patch_metadata(data_json, data_json['aliases'][0], key=ff_key)
        # else:
        #     ff_utils.post_metadata(data_json, type, key=ff_key)

        logger.info('> Posted %s' % data_json['aliases'][0])

    if verbose:
        logger.info(json.dumps(data_json, sort_keys=True, indent=2))

###############################################################
#   _yaml_to_json
###############################################################
def _yaml_to_json(data_yaml, YAMLClass, validate, **kwargs):
    """
    """
    if validate:
        logger.info('> Validating %s' % data_yaml.get('name'))
        try:
            YAMLClass(data_yaml).to_json(**kwargs)
        except yaml_parser.SchemaError:
            pass
    else:
        logger.info('> Processing %s' % data_yaml.get('name'))
        return YAMLClass(data_yaml).to_json(**kwargs)

    return

###############################################################
#   _post_patch_software
###############################################################
def _post_patch_software(ff_key, repo, project, institution,
                         verbose, debug, validate,
                         filepath='portal_objects/software.yaml'):
    """
    """
    logger.info('@ Software...')

    # Set general variables
    filepath_ = f'{repo}/{filepath}'

    # Check
    if not os.path.isfile(filepath_):
        logger.error(f'WARNING: {filepath} not found in {repo}')
        return

    # Create JSON objects
    for d in yaml_parser.load_yaml(filepath_):
        # creating JSON object
        d_ = _yaml_to_json(
                    d, yaml_parser.YAMLSoftware, validate,
                    INSTITUTION=institution, PROJECT=project
                    )
        # post/patch object
        if d_:
            _post_patch_routine(d_, 'Software', ff_key, verbose, debug)

###############################################################
#   _post_patch_file_format
###############################################################
def _post_patch_file_format(ff_key, repo, project, institution,
                            verbose, debug, validate,
                            filepath='portal_objects/file_format.yaml'):
    """
    """
    logger.info('@ FileFormat...')

    # Set general variables
    filepath_ = f'{repo}/{filepath}'

    # Check
    if not os.path.isfile(filepath_):
        logger.error(f'WARNING: {filepath} not found in {repo}')
        return

    # Create JSON objects
    for d in yaml_parser.load_yaml(filepath_):
        # creating JSON object
        d_ = _yaml_to_json(
                    d, yaml_parser.YAMLFileFormat, validate,
                    INSTITUTION=institution,
                    PROJECT=project
                    )
        # post/patch object
        if d_:
            _post_patch_routine(d_, 'FileFormat', ff_key, verbose, debug)

###############################################################
#   _post_patch_file_reference
###############################################################
def _post_patch_file_reference(ff_key, repo, project, institution,
                               verbose, debug, validate,
                               filepath='portal_objects/file_reference.yaml'):
    """
    """
    logger.info('@ FileReference...')

    # Set general variables
    filepath_ = f'{repo}/{filepath}'

    # Check
    if not os.path.isfile(filepath_):
        logger.error(f'WARNING: {filepath} not found in {repo}')
        return

    # Create JSON objects
    for d in yaml_parser.load_yaml(filepath_):
        # creating JSON object
        d_ = _yaml_to_json(
                    d, yaml_parser.YAMLFileReference, validate,
                    INSTITUTION=institution,
                    PROJECT=project
                    )
        # post/patch object
        if d_:
            _post_patch_routine(d_, 'FileReference', ff_key, verbose, debug)

###############################################################
#   _post_patch_workflow
###############################################################
def _post_patch_workflow(ff_key, repo, project, institution,
                         version, pipeline, wfl_bucket,
                         verbose, debug, validate,
                         filepath='portal_objects/workflows'):
    """
    """
    logger.info('@ Workflow...')

    # Set general variables
    filepath_ = f'{repo}/{filepath}'

    # Check
    if not os.path.isdir(filepath_):
        logger.error(f'WARNING: {filepath} not found in {repo}')
        return

    # Create JSON objects
    for fn in glob.glob(f'{filepath_}/*.yaml'):
        for d in yaml_parser.load_yaml(fn):
            # creating JSON object
            d_ = _yaml_to_json(
                        d, yaml_parser.YAMLWorkflow, validate,
                        VERSION=version,
                        INSTITUTION=institution,
                        PROJECT=project,
                        WFLBUCKET_URL=f'{wfl_bucket}/{pipeline}/{version}'
                        )
            # post/patch object
            if d_:
                _post_patch_routine(d_, 'Workflow', ff_key, verbose, debug)

###############################################################
#   _post_patch_metaworkflow
###############################################################
def _post_patch_metaworkflow(ff_key, repo, project, institution,
                             version, verbose, debug, validate,
                             filepath='portal_objects/metaworkflows'):
    """
    """
    logger.info('@ MetaWorkflow...')

    # Set general variables
    filepath_ = f'{repo}/{filepath}'

    # Check
    if not os.path.isdir(filepath_):
        logger.error(f'WARNING: {filepath} not found in {repo}')
        return

    # Create JSON objects
    for fn in glob.glob(f'{filepath_}/*.yaml'):
        for d in yaml_parser.load_yaml(fn):
            # creating JSON object
            d_ = _yaml_to_json(
                        d, yaml_parser.YAMLMetaWorkflow, validate,
                        VERSION=version,
                        INSTITUTION=institution,
                        PROJECT=project
                        )
            # post/patch object
            if d_:
                _post_patch_routine(d_, 'MetaWorkflow', ff_key, verbose, debug)

###############################################################
#   _post_patch_wfl
###############################################################
def _post_patch_wfl(version, repo, pipeline, account,
                    region, wfl_bucket, sentieon_server,
                    debug=False, filepath='wfl', kms_key_id=None):
    """
    """
    logger.info('@ Workflow Description...')

    # Set general variables
    filepath_ = f'{repo}/{filepath}'
    upload_ = f'{filepath_}/upload'
    account_ = f'{account}.dkr.ecr.{region}.amazonaws.com'
    update_ = {
        'ServerSideEncryption': 'aws:kms',
        'SSEKMSKeyId': kms_key_id
        }

    # Check
    if not os.path.isdir(filepath_):
        logger.error(f'WARNING: {filepath} not found in {repo}')
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
        s3_file_ = f'{pipeline}/{version}/{fn}'
        if not debug:
            # create modified description file for upload
            with open(file_, 'r') as read_:
                with open(upload_file_, 'w') as write_:
                    # replace generic variables
                    for line in read_:
                        line = line.replace('ACCOUNT', account_)
                        line = line.replace('VERSION', version)
                        line = line.replace('LICENSEID', sentieon_server)
                        write_.write(line)
            # upload to s3
            extra_args = {'ACL': 'public-read'}  # note that this is no longer public if using encryption!
            if kms_key_id:
                extra_args.update(update_)
            s3.meta.client.upload_file(upload_file_, wfl_bucket, s3_file_, ExtraArgs=extra_args)
            # delete file to allow tmp folder to be deleted at the end
            os.remove(upload_file_)

    # Clean tmp directory
    os.rmdir(upload_)

###############################################################
#   _post_patch_ecr
###############################################################
def _post_patch_ecr(version, repo, account, region, debug=False, filepath='dockerfiles'):
    """
    """
    logger.info('@ Docker Image...')

    # Set general variables
    filepath_ = f'{repo}/{filepath}'
    account_ = f'{account}.dkr.ecr.{region}.amazonaws.com'

    # Check
    if not os.path.isdir(filepath_):
        logger.error(f'WARNING: {filepath} not found in {repo}')
        return

    # Generic bash commands to be modified to correct version and account information
    for fn in glob.glob(f'{filepath_}/*'):
        logger.info('> Processing %s' % fn)
        if not debug:
            # set specific variables
            tag_ = f'{account_}/{fn}:{version}'
            path_ = f'{filepath_}/{fn}'
            image = f"""
                        aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_}
                        docker build -t {tag_} {path_} --no-cache
                        docker push {tag_}
                    """ # note that we are ALWAYS doing no-cache builds so that we can get updated base images whenever applicable
            subprocess.check_call(cmd, shell=True)

################################################
#   _post_patch_repo
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
################################################
def _post_patch_repo(ff_key, repo, wfl_bucket, account, region,
                     project, institution,
                     post_software, post_file_format, post_file_reference,
                     post_workflow, post_metaworkflow, post_wfl, post_ecr,
                     sentieon_server, verbose, debug, validate,
                     version='VERSION', pipeline='PIPELINE', kms_key_id=None):
    """
        post | patch metadata and docker from a pipeline repo
            to the specified environment (ff_key)

        the repo must follow the structure described in the header
    """

    # Get pipeline version
    with open(repo + '/' + version) as f:
        version = f.readlines()[0].strip()
    # Get pipeline name
    with open(repo + '/' + pipeline) as f:
        pipeline = f.readlines()[0].strip()

    # Software
    if post_software:
        _post_patch_software(ff_key, repo, project,
                             institution, verbose, debug, validate)

    # FileFormat
    if post_file_format:
        _post_patch_file_format(ff_key, repo, project,
                                institution, verbose, debug, validate)

    # FileReference
    if post_file_reference:
        _post_patch_file_reference(ff_key, repo, project,
                                   institution, verbose, debug, validate)

    # Workflow
    if post_workflow:
        _post_patch_workflow(ff_key, repo, project, institution,
                             version, pipeline, wfl_bucket, verbose, debug, validate)

    # Metaworkflow
    if post_metaworkflow:
        _post_patch_metaworkflow(ff_key, repo, project, institution,
                                 version, verbose, debug, validate)

    # Wfl
    if post_wfl:
        _post_patch_wfl(version, repo, pipeline, account,
                        region, wfl_bucket, sentieon_server,
                        debug=debug, kms_key_id=kms_key_id)

    # ECR
    if post_ecr:
        _post_patch_ecr(version, repo, account, region, debug=debug)


################################################
#  MAIN
################################################
def main(args):
    """
        deploy cgap pipeline
        post | patch metadata and dockers in the specified environment from repos
    """
    # # Get credentials
    # if os.environ.get('GLOBAL_BUCKET_ENV') and os.environ.get('S3_ENCRYPT_KEY'):  # new cgap account
    #     s3 = s3_utils.s3Utils(env=args.ff_env)
    #     ff_key = s3.get_access_keys('access_key_admin')
    # elif os.environ.get('S3_ENCRYPT_KEY'):  # main account, also need the key to get auth this way
    #     ff_key = ff_utils.get_authentication_with_server(ff_env=args.ff_env)
    # else:
    #     # read key for portal auth from args.keydicts_json [~/.cgap-keydicts.json]
    #     try:
    #         with open(os.path.expanduser(args.keydicts_json)) as keyfile:
    #             keys = json.load(keyfile)
    #     except Exception:
    #         error = 'ERROR, could not locate file with key dicts for portal auth --keydicts-json\n'
    #         sys.exit(error)
    #     ff_key = keys.get(args.ff_env)
    #
    # # Get encryption key
    # kms_key_id = os.environ.get('S3_ENCRYPT_KEY_ID', None)
    # # Check args
    # if not ff_key:
    #     error = 'ERROR, missing key for {0} environment in key dicts for auth\n'.format(args.ff_env)
    #     sys.exit(error)

    kms_key_id, ff_key = '', {}

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

    # Run patching for repo
    for repo in args.repos:
        _post_patch_repo(ff_key, repo, args.wfl_bucket, args.account, args.region,
                         args.project, args.institution,
                         args.post_software, args.post_file_format, args.post_file_reference,
                         args.post_workflow, args.post_metaworkflow,
                         args.post_wfl, args.post_ecr, args.sentieon_server,
                         args.verbose, args.debug, args.validate, kms_key_id=kms_key_id)
