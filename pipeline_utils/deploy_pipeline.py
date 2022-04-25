#!/usr/bin/env python3

################################################
#
#   deploy_pipeline
#
#   Michele Berselli - berselli.michele@gmail.com
#   Phil Grayson - phil.d.grayson@gmail.com
#
################################################

import os, sys, subprocess
import json
from dcicutils import ff_utils, s3_utils
import boto3


def _post_patch_routine(mdata_json, type, ff_key):
    """
        routine to do the post | patching action
    """

    is_patch = True
    try:
        ff_utils.get_metadata(mdata_json['uuid'], key=ff_key)
    except Exception:
        is_patch = False

    if is_patch:
        ff_utils.patch_metadata(mdata_json, mdata_json['uuid'], key=ff_key)
    else:
        ff_utils.post_metadata(mdata_json, type, key=ff_key)


def _post_patch_software(ff_key, repo, project_uuid, institution_uuid,
                         filepath='portal_objects/software.json'):
    """
        routine to post | patch software
    """
    if not os.path.isfile(repo + '/' + filepath): return

    print('Processing software...')
    with open(repo + '/' + filepath) as f:
        d = json.load(f)

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)
        _post_patch_routine(dd, 'Software', ff_key)


def _post_patch_file_format(ff_key, repo, project_uuid, institution_uuid,
                            filepath='portal_objects/file_format.json'):
    """
        routine to post | patch file format
    """
    if not os.path.isfile(repo + '/' + filepath): return

    print('Processing file format...')
    with open(repo + '/' + filepath) as f:
        d = json.load(f)

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)
        _post_patch_routine(dd, 'FileFormat', ff_key)


def _post_patch_file_reference(ff_key, repo, project_uuid, institution_uuid,
                               filepath='portal_objects/file_reference.json'):
    """
        routine to post | patch file reference
    """
    if not os.path.isfile(repo + '/' + filepath): return

    print('Processing file reference...')
    with open(repo + '/' + filepath) as f:
        d = json.load(f)

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)
        _post_patch_routine(dd, 'FileReference', ff_key)


def _post_patch_workflow(ff_key, repo, project_uuid, institution_uuid,
                         version, pipeline,
                         region, cwl_bucket, del_prev_version,
                         filepath='portal_objects/workflows'):
    """
        routine to post | patch workflow
    """
    if not os.path.isdir(repo + '/' + filepath): return

    print('Processing workflow...')
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.json'):
            print('  processing file %s' % fn)
            with open(os.path.join(repo + '/' + filepath, fn), 'r') as f:
                d = json.load(f)

            # clean previous_version and aliases if del_prev_version
            if del_prev_version:
                if d.get('previous_version'):
                    del d['previous_version']
                if d.get('aliases'):
                    d['aliases'] = [d['aliases'][0]]

            # replace VERSION variable with correct version
            d['aliases'][0] = d['aliases'][0].replace('VERSION', version)

            for k in ['app_version', 'name']:
                d[k] = d[k].replace('VERSION', version)

            # replace CWLBUCKET and VERSION variables in cwl_directory_url_v1
            d['cwl_directory_url_v1'] = d['cwl_directory_url_v1'].replace('CWLBUCKET', cwl_bucket).replace('PIPELINE', pipeline).replace('VERSION', version)

            # replace PROJECT_UUID and INSTITUTION_UUID variables
            d['project'] = d['project'].replace('PROJECT_UUID', project_uuid)
            d['institution'] = d['institution'].replace('INSTITUTION_UUID', institution_uuid)

            _post_patch_routine(d, 'Workflow', ff_key)


def _post_patch_metaworkflow(ff_key, repo, project_uuid, institution_uuid,
                             version, del_prev_version,
                             filepath='portal_objects/metaworkflows'):
    """
        routine to post | patch metaworkflow
    """
    if not os.path.isdir(repo + '/' + filepath): return

    print('Processing metaworkflow...')
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.json'):
            print('  processing file %s' % fn)
            with open(os.path.join(repo + '/' + filepath, fn), 'r') as f:
                d = json.load(f)
                for k in ['title', 'version']:
                    d[k] = d[k].replace('VERSION', version)

            # clean previous_version if del_prev_version
            if del_prev_version:
                if d.get('previous_version'):
                    del d['previous_version']

            # replace PROJECT_UUID and INSTITUTION_UUID variables
            d['project'] = d['project'].replace('PROJECT_UUID', project_uuid)
            d['institution'] = d['institution'].replace('INSTITUTION_UUID', institution_uuid)

            _post_patch_routine(d, 'MetaWorkflow', ff_key)


def _post_patch_cwl(version, repo, pipeline, account,
                    region, cwl_bucket,
                    filepath='cwl', kms_key_id=None):
    """
        routine to post | patch cwl
    """
    if not os.path.isdir(repo + '/' + filepath): return

    print('Processing cwl files...')
    s3 = boto3.resource('s3')
    # mk tmp dir for modified cwls
    os.mkdir(repo + '/' + filepath + '/upload')
    account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.cwl'):
            # set original file path and path for s3
            file_path = repo + '/' + filepath + '/' + fn
            s3_path_and_file = pipeline + '/' + version + '/'+ fn

            # separate workflows, which can be automatically uploaded to s3 without edits ...
            if fn.startswith('workflow'):
                print('  processing file %s' % fn)
                extra_args = {'ACL': 'public-read'}  # note that this is no longer public if using encryption!
                if kms_key_id:
                    extra_args.update({
                        'ServerSideEncryption': 'aws:kms',
                        'SSEKMSKeyId': kms_key_id
                    })
                s3.meta.client.upload_file(file_path, cwl_bucket, s3_path_and_file, ExtraArgs=extra_args)

            # ... from CommandLineTool files which have the dockerPull that needs modification
            else:
                print('  processing file %s' % fn)
                with open(file_path, 'r') as f:
                    with open(repo + '/' + filepath + '/upload/' + fn, 'w') as w:
                        for line in f:
                            if 'dockerPull' in line:
                                # modify line for output file by replacing generic variables
                                line = line.replace('ACCOUNT', account_region).replace('VERSION', version)
                            w.write(line)

                # once modified, upload to s3
                upload_path_and_file = repo + '/' + filepath + '/upload/' + fn
                extra_args = {'ACL': 'public-read'}  # note that this is no longer public if using encryption!
                if kms_key_id:
                    extra_args.update({
                        'ServerSideEncryption': 'aws:kms',
                        'SSEKMSKeyId': kms_key_id
                    })
                s3.meta.client.upload_file(upload_path_and_file, cwl_bucket, s3_path_and_file, ExtraArgs=extra_args)

                # delete file to allow tmp folder to be deleted at the end
                os.remove(upload_path_and_file)

    # clean the directory from github repo
    os.rmdir(repo + '/' + filepath + '/upload')


def _post_patch_ecr(version, repo, account, region,
                    filepath='dockerfiles'):
    """
        routine to build the docker image and push it to ECR
    """
    if not os.path.isdir(repo + '/' + filepath): return

    print('Processing docker image...')
    account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
    # generic bash commands to be modified to correct version and account information
    for fn in os.listdir(repo + '/' + filepath):
        print('  processing docker %s' % fn)
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
#       cwl
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
def _post_patch_repo(ff_key, repo, cwl_bucket, account, region,
                     project_uuid, institution_uuid,
                     post_software, post_file_format, post_file_reference,
                     post_workflow, post_metaworkflow,
                     post_cwl, post_ecr, del_prev_version,
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
        _post_patch_software(ff_key, repo, project_uuid, institution_uuid)

    # File format
    if post_file_format:
        _post_patch_file_format(ff_key, repo, project_uuid, institution_uuid)

    # File reference
    if post_file_reference:
        _post_patch_file_reference(ff_key, repo, project_uuid, institution_uuid)

    # Workflow
    if post_workflow:
        _post_patch_workflow(ff_key, repo, project_uuid, institution_uuid,
                             version, pipeline,
                             region, cwl_bucket, del_prev_version)

    # Metaworkflow
    if post_metaworkflow:
        _post_patch_metaworkflow(ff_key, repo, project_uuid, institution_uuid,
                                 version, del_prev_version)

    # Cwl
    if post_cwl:
        _post_patch_cwl(version, repo, pipeline, account,
                        region, cwl_bucket, kms_key_id=kms_key_id)

    # ECR
    if post_ecr:
        _post_patch_ecr(version, repo, account, region)


def main(args):
    """
        deploy cgap pipeline
        post | patch metadata and dockers in the specified environment from repos
    """
    # Get credentials
    if os.environ.get('GLOBAL_BUCKET_ENV') and os.environ.get('S3_ENCRYPT_KEY'):  # new cgap account
        s3 = s3_utils.s3Utils(env=args.ff_env)
        ff_key = s3.get_access_keys('access_key_admin')
    elif os.environ.get('S3_ENCRYPT_KEY'):  # main account, also need the key to get auth this way
        ff_key = ff_utils.get_authentication_with_server(ff_env=args.ff_env)
    else:
        # read key for portal auth from args.keydicts_json [~/.cgap-keydicts.json]
        try:
            with open(os.path.expanduser(args.keydicts_json)) as keyfile:
                keys = json.load(keyfile)
        except Exception:
            error = 'ERROR, could not locate file with key dicts for portal auth --keydicts-json\n'
            sys.exit(error)
        ff_key = keys.get(args.ff_env)

    # Get encryption key
    kms_key_id = os.environ.get('S3_ENCRYPT_KEY_ID', None)
    # Check args
    if not ff_key:
        error = 'ERROR, missing key for {0} environment in key dicts for auth\n'.format(args.ff_env)
        sys.exit(error)

    if not args.cwl_bucket:
        if args.post_workflow or args.post_cwl:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow requires --cwl-bucket argument\n'
            sys.exit(error)

    if not args.account:
        if args.post_workflow or args.post_cwl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow | --post-ecr requires --account argument\n'
            sys.exit(error)

    if not args.region:
        if args.post_workflow or args.post_cwl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow | --post-ecr requires --region argument\n'
            sys.exit(error)

    if not args.project_uuid:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --project-uuid argument\n'
            sys.exit(error)

    if not args.institution_uuid:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --institution-uuid argument\n'
            sys.exit(error)

    # Run patching for repo
    for repo in args.repos:
        _post_patch_repo(ff_key, repo, args.cwl_bucket, args.account, args.region,
                         args.project_uuid, args.institution_uuid,
                         args.post_software, args.post_file_format, args.post_file_reference,
                         args.post_workflow, args.post_metaworkflow,
                         args.post_cwl, args.post_ecr, args.del_prev_version, kms_key_id=kms_key_id)
