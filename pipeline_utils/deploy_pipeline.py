#!/usr/bin/env python3

################################################
#
#   deploy_pipeline
#
#   Michele Berselli
#   berselli.michele@gmail.com
#
################################################


################################################
#   Libraries
################################################
import os, sys, argparse, subprocess
import json
from dcicutils import ff_utils, s3_utils
import boto3


################################################
#   Functions
################################################
################################################
#   _post_patch_routine
################################################
def _post_patch_routine(mdata_json, type, ff_key):
    '''
        routine to do the post | patching action

        note: this can be re-written to replace try/except with query to database to decide if post or patch
    '''
    try:
        ff_utils.post_metadata(mdata_json, type, key=ff_key)
    except Exception:
        ff_utils.patch_metadata(mdata_json, mdata_json['uuid'], key=ff_key)

    # try:
    #     ff_utils.post_metadata(mdata_json, type, key=ff_key)
    # except Exception as e:
    #     if 'Keys conflict' in str(e):
    #         if ignore_key_conflict:
    #             pass
    #         else:
    #             raise(e)
    #     else:
    #         ff_utils.patch_metadata(mdata_json, mdata_json['uuid'], key=ff_key)

################################################
#   _post_patch_software
################################################
def _post_patch_software(ff_key, project_uuid, institution_uuid,
                         filepath='portal_objects/software.json'):
    '''
        routine to post | patch software
    '''
    print('Processing software...')
    with open(filepath) as f:
        d = json.load(f)

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)

        # patch
        _post_patch_routine(dd, 'Software', ff_key)

################################################
#   _post_patch_file_format
################################################
def _post_patch_file_format(ff_key, project_uuid, institution_uuid,
                            filepath='portal_objects/file_format.json'):
    '''
        routine to post | patch file format
    '''
    print('Processing file format...')
    with open(filepath) as f:
        d = json.load(f)

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)

        # patch
        _post_patch_routine(dd, 'FileFormat', ff_key)

################################################
#   _post_patch_file_reference
################################################
def _post_patch_file_reference(ff_key, project_uuid, institution_uuid,
                               filepath='portal_objects/file_reference.json'):
    '''
        routine to post | patch file reference
    '''
    print('Processing file reference...')
    with open(filepath) as f:
        d = json.load(f)

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)

        # patch
        _post_patch_routine(dd, 'FileReference', ff_key)

################################################
#   _post_patch_workflow
################################################
def _post_patch_workflow(ff_key, project_uuid, institution_uuid,
                         version, pipeline, account,
                         region, cwl_bucket, del_prev_version,
                         filepath='portal_objects/workflow'):
    '''
        routine to post | patch workflow
    '''
    print('Processing workflow...')
    for fn in os.listdir(filepath):
        if fn.endswith('.json'):
            print('  processing file %s' % fn)
            with open(os.path.join(filepath, fn), 'r') as f:
                d = json.load(f)

            # clean previous_version and aliases if del_prev_version
            if del_prev_version:
                if d.get('previous_version'):
                    del d['previous_version']
                if d.get('aliases'):
                    d['aliases'] = [d['aliases'][0]]

            # replace VERSION variable with correct version
            d['aliases'][0] = d['aliases'][0].replace('VERSION', version)

            for k in ['app_version', 'docker_image_name', 'name']:
                d[k] = d[k].replace('VERSION', version)

            # replace CWLBUCKET and VERSION variables in cwl_directory_url_v1
            d['cwl_directory_url_v1'] = d['cwl_directory_url_v1'].replace('CWLBUCKET', cwl_bucket).replace('PIPELINE', pipeline).replace('VERSION', version)

            # replace ACCOUNT and VERSION variables for docker_image_name
            account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
            d['docker_image_name'] = d['docker_image_name'].replace('ACCOUNT', account_region).replace('VERSION', version)

            # replace PROJECT_UUID and INSTITUTION_UUID variables
            d['project'] = d['project'].replace('PROJECT_UUID', project_uuid)
            d['institution'] = d['institution'].replace('INSTITUTION_UUID', institution_uuid)

            # patch
            _post_patch_routine(d, 'Workflow', ff_key)

################################################
#   _post_patch_metaworkflow
################################################
def _post_patch_metaworkflow(ff_key, project_uuid, institution_uuid,
                             version, del_prev_version,
                             filepath='portal_objects/metaworkflows'):
    '''
        routine to post | patch metaworkflow
    '''
    print('Processing metaworkflow...')
    for fn in os.listdir(filepath):
        if fn.endswith('.json'):
            print('  processing file %s' % fn)
            with open(os.path.join(filepath, fn), 'r') as f:
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

            # patch
            _post_patch_routine(d, 'MetaWorkflow', ff_key)

################################################
#   _post_patch_cwl
################################################
def _post_patch_cwl(version, pipeline, account,
                    region, cwl_bucket, del_prev_version,
                    filepath='cwl'):
    '''
        routine to post | patch cwl
    '''
    print('Processing cwl files...')
    s3 = boto3.resource('s3')
    # mk tmp dir for modified cwls
    os.mkdir(filepath + '/upload')
    account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
    for fn in os.listdir(filepath):
        if fn.endswith('.cwl'):
            # set original file path and path for s3
            file_path = filepath + '/' + fn
            s3_path_and_file = pipeline + '/' + version + '/'+ fn

            # separate workflows, which can be automatically uploaded to s3 without edits ...
            if fn.startswith('workflow'):
                print('  processing file %s' % fn)
                s3.meta.client.upload_file(file_path, cwl_bucket, s3_path_and_file, ExtraArgs={'ACL':'public-read'})

            # ... from CommandLineTool files which have the dockerPull that needs modification
            else:
                print('  processing file %s' % fn)
                with open(file_path, 'r') as f:
                    with open(filepath + '/upload/' + fn, 'w') as w:
                        for line in f:
                            if 'dockerPull' in line:
                                # modify line for output file by replacing generic variables
                                line = line.replace('ACCOUNT', account_region).replace('VERSION', version)
                            w.write(line)
                # once modified, upload to s3
                upload_path_and_file = filepath + '/upload/' + fn
                s3.meta.client.upload_file(upload_path_and_file, cwl_bucket, s3_path_and_file, ExtraArgs={'ACL':'public-read'})

                # delete file to allow tmp folder to be deleted at the end
                os.remove(upload_path_and_file)

    # clean the directory from github repo
    os.rmdir(filepath + '/upload')

################################################
#   _post_patch_ecr
################################################
def _post_patch_ecr(version, account, region,
                    filepath='dockerfiles'):
    '''
        routine to build the docker image and push it to ECR
    '''
    print('Processing docker image...')
    account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
    # generic bash commands to be modified to correct version and account information
    for fn in os.listdir(filepath):
        print('  processing docker %s' % fn)
        tag = account_region + '/' + fn + ':' + version
        path = filepath + '/' + fn
        image = '''
            aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT

            docker build -t TAG PATH
            docker push TAG
        '''
        cmd = image.replace('REGION', region).replace('TAG', tag).replace('ACCOUNT', account).replace('PATH', path)
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
def _post_patch_repo(ff_key, cwl_bucket, account, region,
                     project_uuid, institution_uuid,
                     post_software, post_file_format, post_file_reference,
                     post_workflow, post_metaworkflow,
                     post_cwl, post_ecr, del_prev_version,
                     version='VERSION', pipeline='PIPELINE'):
    '''
        post | patch metadata and docker from a pipeline repo
            to the specified environment (ff_key)

        the repo must follow the structure described in the header
    '''

    # Get pipeline version
    with open(version) as f:
        version = f.readlines()[0].strip()
    # Get pipeline name
    with open(pipeline) as f:
        pipeline = f.readlines()[0].strip()

    # Software
    if post_software:
        _post_patch_software(ff_key, project_uuid, institution_uuid)

    # File format
    if post_file_format:
        _post_patch_file_format(ff_key, project_uuid, institution_uuid)

    # File reference
    if post_file_reference:
        _post_patch_file_reference(ff_key, project_uuid, institution_uuid)

    # Workflow
    if post_workflow:
        _post_patch_workflow(ff_key, project_uuid, institution_uuid,
                             version, pipeline, account,
                             region, cwl_bucket, del_prev_version)

    # Metaworkflow
    if post_metaworkflow:
        _post_patch_metaworkflow(ff_key, project_uuid, institution_uuid,
                                 version, del_prev_version)

    # Cwl
    if post_cwl:
        _post_patch_cwl(version, pipeline, account,
                        region, cwl_bucket, del_prev_version)

    # ECR
    if post_ecr:
        _post_patch_ecr(version, account, region)


################################################
#   main
################################################
def main(args):
    '''
        deploy cgap pipeline
        post | patch metadata and dockers in the specified environment from repos
    '''

    # Get env variables
    if os.environ.get('GLOBAL_BUCKET_ENV', ''):  # new cgap account
        s3 = s3_utils.s3Utils(env=ff_env)
        ff_key = s3.get_access_keys('access_key_admin')
    else:
        ff_key = ff_utils.get_authentication_with_server(ff_env=args.ff_env)

    # Check args
    if not args.cwl_bucket:
        if args.post_workflow or args.post_cwl:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow requires --cwl-bucket argument'
            sys.exit(error)

    if not args.account:
        if args.post_workflow or args.post_cwl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow | --post-ecr requires --account argument'
            sys.exit(error)

    if not args.region:
        if args.post_workflow or args.post_cwl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow | --post-ecr requires --region argument'
            sys.exit(error)

    if not args.project_uuid:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --project-uuid argument'
            sys.exit(error)

    if not args.institution_uuid:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --institution-uuid argument'
            sys.exit(error)


    # Run patching for repo
    _post_patch_repo(ff_key, args.cwl_bucket, args.account, args.region,
                     args.project_uuid, args.institution_uuid,
                     args.post_software, args.post_file_format, args.post_file_reference,
                     args.post_workflow, args.post_metaworkflow,
                     args.post_cwl, args.post_ecr, args.del_prev_version)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # Required args
    parser.add_argument('--ff-env', required=True)
    parser.add_argument('--cwl-bucket', required=False)
    parser.add_argument('--account', required=False)
    parser.add_argument('--region', required=False)
    parser.add_argument('--project-uuid', required=False)
    parser.add_argument('--institution-uuid', required=False)

    # Optional args
    parser.add_argument('--post-software', action='store_true')
    parser.add_argument('--post-file-format', action='store_true')
    parser.add_argument('--post-file-reference', action='store_true')
    parser.add_argument('--post-workflow', action='store_true')
    parser.add_argument('--post-metaworkflow', action='store_true')
    parser.add_argument('--post-cwl', action='store_true')
    parser.add_argument('--post-ecr', action='store_true')
    parser.add_argument('--del-prev-version', action='store_true')

    args = parser.parse_args()

    main(args)
