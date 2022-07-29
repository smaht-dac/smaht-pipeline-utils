#!/usr/bin/env python3

################################################
#
#   deploy_pipeline, from Yaml format
#
#   Michele Berselli - berselli.michele@gmail.com
#   Phil Grayson - phil.d.grayson@gmail.com
#
################################################

import os, sys, subprocess
import json
import boto3
from jsonschema import validate
from dcicutils import ff_utils, s3_utils
from pipeline_utils.lib import yaml_parser

# schemas
from pipeline_utils.schemas.YamlWfl import YamlWfl_schema
from pipeline_utils.schemas.YamlMWfl import YamlMWfl_schema
from pipeline_utils.schemas.YamlSftwr import YamlSftwr_schema
from pipeline_utils.schemas.YamlRef import YamlRef_schema
from pipeline_utils.schemas.YamlFrmt import YamlFrmt_schema


def _post_patch_routine(mdata_json, type, ff_key, verbose=False, debug=False):
    """
        routine to do the post | patching action
    """
    if not debug:
        pass
        # is_patch = True
        # try:
        #     ff_utils.get_metadata(mdata_json['uuid'], key=ff_key)
        # except Exception:
        #     is_patch = False
        #
        # if is_patch:
        #     ff_utils.patch_metadata(mdata_json, mdata_json['uuid'], key=ff_key)
        # else:
        #     ff_utils.post_metadata(mdata_json, type, key=ff_key)

    sys.stdout.write('--> posted %s\n' % mdata_json['aliases'][0])

    if verbose:
        sys.stdout.write('\n')
        sys.stdout.write(json.dumps(mdata_json, sort_keys=True, indent=2))
        sys.stdout.write('\n\n')


def _post_patch_software(ff_key, repo, project_id, institution_id,
                         verbose, debug, filepath='portal_objects/software.yaml'):
    """
        routine to post | patch software
    """
    if not os.path.isfile(repo + '/' + filepath): return

    sys.stdout.write('Processing Software...\n')
    for d in yaml_parser.load_yaml(repo + '/' + filepath):
        # validating object vs schema
        validate(instance=d, schema=YamlSftwr_schema)
        # creating YamlSftwr object
        yamlsftwr = yaml_parser.YamlSftwr(d)
        # creating json object
        d_ = yamlsftwr.to_json(
                    INSTITUTION=institution_id,
                    PROJECT=project_id
                    )
        # post patch
        _post_patch_routine(d_, 'Software', ff_key, verbose, debug)


def _post_patch_file_format(ff_key, repo, project_id, institution_id,
                            verbose, debug, filepath='portal_objects/file_format.yaml'):
    """
        routine to post | patch file format
    """
    if not os.path.isfile(repo + '/' + filepath): return

    sys.stdout.write('Processing FileFormat...\n')
    for d in yaml_parser.load_yaml(repo + '/' + filepath):
        # # validating object vs schema
        validate(instance=d, schema=YamlFrmt_schema)
        # creating YamlFrmt object
        yamlfrmt = yaml_parser.YamlFrmt(d)
        # creating json object
        d_ = yamlfrmt.to_json(
                    INSTITUTION=institution_id,
                    PROJECT=project_id
                    )
        # post patch
        _post_patch_routine(d_, 'FileFormat', ff_key, verbose, debug)


def _post_patch_file_reference(ff_key, repo, project_id, institution_id,
                               verbose, debug, filepath='portal_objects/file_reference.yaml'):
    """
        routine to post | patch file reference
    """
    if not os.path.isfile(repo + '/' + filepath): return

    sys.stdout.write('Processing FileReference...\n')
    for d in yaml_parser.load_yaml(repo + '/' + filepath):
        # # validating object vs schema
        validate(instance=d, schema=YamlRef_schema)
        # creating YamlRef object
        yamlref = yaml_parser.YamlRef(d)
        # creating json object
        d_ = yamlref.to_json(
                    INSTITUTION=institution_id,
                    PROJECT=project_id
                    )
        # post patch
        _post_patch_routine(d_, 'FileReference', ff_key, verbose, debug)


def _post_patch_workflow(ff_key, repo, project_id, institution_id,
                         version, pipeline, region, wfl_bucket,
                         verbose, debug, filepath='portal_objects/workflows'):
    """
        routine to post | patch workflow
    """
    if not os.path.isdir(repo + '/' + filepath): return

    sys.stdout.write('Processing Workflow...\n')
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.yaml'):
            for d in yaml_parser.load_yaml(os.path.join(repo + '/' + filepath, fn)):
                # validating object vs schema
                validate(instance=d, schema=YamlWfl_schema)
                # creating YamlWfl object
                yamlwfl = yaml_parser.YamlWfl(d)
                wflbucket_url = wfl_bucket + '/' + pipeline + '/' + version
                # creating json object
                d_ = yamlwfl.to_json(
                            VERSION=version,
                            INSTITUTION=institution_id,
                            PROJECT=project_id,
                            WFLBUCKET_URL=wflbucket_url
                            )
                # post patch
                _post_patch_routine(d_, 'Workflow', ff_key, verbose, debug)


def _post_patch_metaworkflow(ff_key, repo, project_id, institution_id,
                             version, verbose, debug,
                             filepath='portal_objects/metaworkflows'):
    """
        routine to post | patch metaworkflow
    """
    if not os.path.isdir(repo + '/' + filepath): return

    sys.stdout.write('Processing MetaWorkflow...\n')
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.yaml'):
            for d in yaml_parser.load_yaml(os.path.join(repo + '/' + filepath, fn)):
                # validating object vs schema
                validate(instance=d, schema=YamlMWfl_schema)
                # creating YamlMWfl object
                yamlmwfl = yaml_parser.YamlMWfl(d)
                # creating json object
                d_ = yamlmwfl.to_json(
                            VERSION=version,
                            INSTITUTION=institution_id,
                            PROJECT=project_id
                            )
                # post patch
                _post_patch_routine(d_, 'MetaWorkflow', ff_key, verbose, debug)


def _post_patch_wfl(version, repo, pipeline, account,
                    region, wfl_bucket, sentieon_server,
                    filepath='wfl', kms_key_id=None):
    """
        routine to post | patch wfl
    """
    if not os.path.isdir(repo + '/' + filepath): return

    sys.stdout.write('Processing Workflow Description...\n')
    s3 = boto3.resource('s3')
    # mk tmp dir for modified wfls
    os.mkdir(repo + '/' + filepath + '/upload')
    account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.cwl') or fn.endswith('.wdl'):
            # set original file path and path for s3
            file_path = repo + '/' + filepath + '/' + fn
            s3_path_and_file = pipeline + '/' + version + '/'+ fn

            # separate workflows, which can be automatically uploaded to s3 without edits ...
            if fn.startswith('workflow'):
                sys.stdout.write('  processing file %s\n' % fn)
                extra_args = {'ACL': 'public-read'}  # note that this is no longer public if using encryption!
                if kms_key_id:
                    extra_args.update({
                        'ServerSideEncryption': 'aws:kms',
                        'SSEKMSKeyId': kms_key_id
                    })
                s3.meta.client.upload_file(file_path, wfl_bucket, s3_path_and_file, ExtraArgs=extra_args)

            # ... from CommandLineTool files which needs modification
            else:
                sys.stdout.write('  processing file %s\n' % fn)
                with open(file_path, 'r') as f:
                    with open(repo + '/' + filepath + '/upload/' + fn, 'w') as w:
                        # modify lines for output file by replacing generic variables
                        for line in f:
                            if 'dockerPull' in line:
                                line = line.replace('ACCOUNT', account_region).replace('VERSION', version)
                            elif 'LICENSEID' in line:
                                line = line.replace('LICENSEID', sentieon_server)
                            w.write(line)

                # upload to s3
                upload_path_and_file = repo + '/' + filepath + '/upload/' + fn
                extra_args = {'ACL': 'public-read'}  # note that this is no longer public if using encryption!
                if kms_key_id:
                    extra_args.update({
                        'ServerSideEncryption': 'aws:kms',
                        'SSEKMSKeyId': kms_key_id
                    })
                s3.meta.client.upload_file(upload_path_and_file, wfl_bucket, s3_path_and_file, ExtraArgs=extra_args)

                # delete file to allow tmp folder to be deleted at the end
                os.remove(upload_path_and_file)

    # clean the directory from github repo
    os.rmdir(repo + '/' + filepath + '/upload')


def _post_patch_ecr(version, repo, account, region, filepath='dockerfiles'):
    """
        routine to build the docker image and push it to ECR
    """
    if not os.path.isdir(repo + '/' + filepath): return

    sys.stdout.write('Processing Docker Image...\n')
    account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
    # generic bash commands to be modified to correct version and account information
    for fn in os.listdir(repo + '/' + filepath):
        sys.stdout.write('  processing docker %s\n' % fn)
        tag = account_region + '/' + fn + ':' + version
        path = repo + '/' + filepath + '/' + fn
        image = """
            aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_REGION

            docker build -t TAG PATH --no-cache
            docker push TAG
        """  # note that we are ALWAYS doing no-cache builds so that we can get updated base images whenever applicable
        cmd = image.replace('ACCOUNT_REGION', account_region).replace('REGION', region).replace('TAG', tag).replace('PATH', path)
        subprocess.check_call(cmd, shell=True)


################################################
#   _post_patch_repo
#
### Expected structure for the pipeline repository
#
#   pipeline
#       wfl
#       dockerfiles
#            image_name
#                Dockerfile
#       portal_objects
#           workflows
#           metaworkflows
#           file_format.json
#           file_reference.json
#           software.json
#       PIPELINE
#       VERSION
#
################################################
def _post_patch_repo(ff_key, repo, wfl_bucket, account, region,
                     project_id, institution_id,
                     post_software, post_file_format, post_file_reference,
                     post_workflow, post_metaworkflow, post_wfl, post_ecr,
                     sentieon_server, verbose, debug,
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
        _post_patch_software(ff_key, repo, project_id,
                             institution_id, verbose, debug)

    # File format
    if post_file_format:
        _post_patch_file_format(ff_key, repo, project_id,
                                institution_id, verbose, debug)

    # File reference
    if post_file_reference:
        _post_patch_file_reference(ff_key, repo, project_id,
                                   institution_id, verbose, debug)

    # Workflow
    if post_workflow:
        _post_patch_workflow(ff_key, repo, project_id, institution_id,
                             version, pipeline, region, wfl_bucket, verbose, debug)

    # Metaworkflow
    if post_metaworkflow:
        _post_patch_metaworkflow(ff_key, repo, project_id, institution_id,
                                 version, verbose, debug)

    # Wfl
    if post_wfl:
        _post_patch_wfl(version, repo, pipeline, account,
                        region, wfl_bucket, sentieon_server, kms_key_id=kms_key_id)

    # ECR
    if post_ecr:
        _post_patch_ecr(version, repo, account, region)


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

    if not args.project_id:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --project-id argument\n'
            sys.exit(error)

    if not args.institution_id:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --institution-id argument\n'
            sys.exit(error)

    # Run patching for repo
    for repo in args.repos:
        _post_patch_repo(ff_key, repo, args.wfl_bucket, args.account, args.region,
                         args.project_id, args.institution_id,
                         args.post_software, args.post_file_format, args.post_file_reference,
                         args.post_workflow, args.post_metaworkflow,
                         args.post_wfl, args.post_ecr, args.sentieon_server,
                         args.verbose, args.debug, kms_key_id=kms_key_id)
