#!/usr/bin/env python3

################################################
#
#   deploy_pipeline
#
#   Michele Berselli - berselli.michele@gmail.com
#   Phil Grayson - phil.d.grayson@gmail.com
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
    #end try

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
    # #end try

################################################
#   _post_patch_software
################################################
def _post_patch_software(ff_key, repo, project_uuid, institution_uuid,
                         filepath='portal_objects/software.json'):
    '''
        routine to post | patch software
    '''
    print('Processing software...')
    with open(repo + '/' + filepath) as f:
        d = json.load(f)
    #end with

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)

        # patch
        _post_patch_routine(dd, 'Software', ff_key)
    #end for

#end def

################################################
#   _post_patch_file_format
################################################
def _post_patch_file_format(ff_key, repo, project_uuid, institution_uuid,
                            filepath='portal_objects/file_format.json'):
    '''
        routine to post | patch file format
    '''
    print('Processing file format...')
    with open(repo + '/' + filepath) as f:
        d = json.load(f)
    #end with

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)

        # patch
        _post_patch_routine(dd, 'FileFormat', ff_key)
    #end for

#end def

################################################
#   _post_patch_file_reference
################################################
def _post_patch_file_reference(ff_key, repo, project_uuid, institution_uuid,
                               filepath='portal_objects/file_reference.json'):
    '''
        routine to post | patch file reference
    '''
    print('Processing file reference...')
    with open(repo + '/' + filepath) as f:
        d = json.load(f)
    #end with

    for dd in d:
        print('  processing uuid %s' % dd['uuid'])

        # replace PROJECT_UUID and INSTITUTION_UUID variables
        dd['project'] = dd['project'].replace('PROJECT_UUID', project_uuid)
        dd['institution'] = dd['institution'].replace('INSTITUTION_UUID', institution_uuid)

        # patch
        _post_patch_routine(dd, 'FileReference', ff_key)
    #end for

#end def

################################################
#   _post_patch_workflow
################################################
def _post_patch_workflow(ff_key, repo, project_uuid, institution_uuid,
                         version, pipeline, account,
                         region, cwl_bucket, del_prev_version,
                         filepath='portal_objects/workflows'):
    '''
        routine to post | patch workflow
    '''
    print('Processing workflow...')
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.json'):
            print('  processing file %s' % fn)
            with open(os.path.join(repo + '/' + filepath, fn), 'r') as f:
                d = json.load(f)
            #end with

            # clean previous_version and aliases if del_prev_version
            if del_prev_version:
                if d.get('previous_version'):
                    del d['previous_version']
                #end if
                if d.get('aliases'):
                    d['aliases'] = [d['aliases'][0]]
                #end if
            #end if

            # replace VERSION variable with correct version
            d['aliases'][0] = d['aliases'][0].replace('VERSION', version)

            for k in ['app_version', 'docker_image_name', 'name']:
                d[k] = d[k].replace('VERSION', version)
            #end for

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
        #end if
    #end for

#end def

################################################
#   _post_patch_metaworkflow
################################################
def _post_patch_metaworkflow(ff_key, repo, project_uuid, institution_uuid,
                             version, del_prev_version,
                             filepath='portal_objects/metaworkflows'):
    '''
        routine to post | patch metaworkflow
    '''
    print('Processing metaworkflow...')
    for fn in os.listdir(repo + '/' + filepath):
        if fn.endswith('.json'):
            print('  processing file %s' % fn)
            with open(os.path.join(repo + '/' + filepath, fn), 'r') as f:
                d = json.load(f)
                for k in ['title', 'version']:
                    d[k] = d[k].replace('VERSION', version)
                #end for
            #end with

            # clean previous_version if del_prev_version
            if del_prev_version:
                if d.get('previous_version'):
                    del d['previous_version']
                #end if
            #end if

            # replace PROJECT_UUID and INSTITUTION_UUID variables
            d['project'] = d['project'].replace('PROJECT_UUID', project_uuid)
            d['institution'] = d['institution'].replace('INSTITUTION_UUID', institution_uuid)

            # patch
            _post_patch_routine(d, 'MetaWorkflow', ff_key)
        #end if
    #end for

#end def

################################################
#   _post_patch_cwl
################################################
def _post_patch_cwl(version, repo, pipeline, account,
                    region, cwl_bucket, del_prev_version,
                    filepath='cwl'):
    '''
        routine to post | patch cwl
    '''
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
                s3.meta.client.upload_file(file_path, cwl_bucket, s3_path_and_file, ExtraArgs={'ACL':'public-read'})

            # ... from CommandLineTool files which have the dockerPull that needs modification
            else:
                print('  processing file %s' % fn)
                with open(file_path, 'r') as f:
                    with open(repo + '/' + filepath + '/upload/' + fn, 'w') as w:
                        for line in f:
                            if 'dockerPull' in line:
                                # modify line for output file by replacing generic variables
                                line = line.replace('ACCOUNT', account_region).replace('VERSION', version)
                            #end if
                            w.write(line)
                        #end for
                    #end with
                #end with
                # once modified, upload to s3
                upload_path_and_file = repo + '/' + filepath + '/upload/' + fn
                s3.meta.client.upload_file(upload_path_and_file, cwl_bucket, s3_path_and_file, ExtraArgs={'ACL':'public-read'})

                # delete file to allow tmp folder to be deleted at the end
                os.remove(upload_path_and_file)
            #end if
        #end if
    #end for

    # clean the directory from github repo
    os.rmdir(repo + '/' + filepath + '/upload')

#end def

################################################
#   _post_patch_ecr
################################################
def _post_patch_ecr(version, repo, account, region,
                    filepath='dockerfiles'):
    '''
        routine to build the docker image and push it to ECR
    '''
    print('Processing docker image...')
    account_region = account + '.dkr.ecr.' + region + '.amazonaws.com'
    # generic bash commands to be modified to correct version and account information
    for fn in os.listdir(repo + '/' + filepath):
        print('  processing docker %s' % fn)
        tag = account_region + '/' + fn + ':' + version
        path = repo + '/' + filepath + '/' + fn
        image = '''
            aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_REGION

            docker build -t TAG PATH
            docker push TAG
        '''
        cmd = image.replace('ACCOUNT_REGION', account_region).replace('REGION', region).replace('TAG', tag).replace('PATH', path)
        subprocess.check_call(cmd, shell=True)
    #end for

#end def

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
                     version='VERSION', pipeline='PIPELINE'):
    '''
        post | patch metadata and docker from a pipeline repo
            to the specified environment (ff_key)

        the repo must follow the structure described in the header
    '''

    # Get pipeline version
    with open(repo + '/' + version) as f:
        version = f.readlines()[0].strip()
    #end with
    # Get pipeline name
    with open(repo + '/' + pipeline) as f:
        pipeline = f.readlines()[0].strip()
    #end with

    # Software
    if post_software:
        _post_patch_software(ff_key, repo, project_uuid, institution_uuid)
    #end if

    # File format
    if post_file_format:
        _post_patch_file_format(ff_key, repo, project_uuid, institution_uuid)
    #end if

    # File reference
    if post_file_reference:
        _post_patch_file_reference(ff_key, repo, project_uuid, institution_uuid)
    #end if

    # Workflow
    if post_workflow:
        _post_patch_workflow(ff_key, repo, project_uuid, institution_uuid,
                             version, pipeline, account,
                             region, cwl_bucket, del_prev_version)
    #end if

    # Metaworkflow
    if post_metaworkflow:
        _post_patch_metaworkflow(ff_key, repo, project_uuid, institution_uuid,
                                 version, del_prev_version)
    #end if

    # Cwl
    if post_cwl:
        _post_patch_cwl(version, repo, pipeline, account,
                        region, cwl_bucket, del_prev_version)
    #end if

    # ECR
    if post_ecr:
        _post_patch_ecr(version, repo, account, region)
    #end if

#end def

################################################
#   runner
################################################
def main(args):
    '''
        deploy cgap pipeline
        post | patch metadata and dockers in the specified environment from repos
    '''

    # Get credentials
    if os.environ.get('GLOBAL_BUCKET_ENV') and os.environ.get('S3_ENCRYPT_KEY'):  # new cgap account
        s3 = s3_utils.s3Utils(env=ff_env)
        ff_key = s3.get_access_keys('access_key_admin')
    elif os.environ.get('S3_ENCRYPT_KEY'):  # main account, also need the key to get auth this way
        ff_key = ff_utils.get_authentication_with_server(ff_env=args.ff_env)
    else:
        # read key for portal auth from args.keydicts_json [~/.cgap-keydicts.json]
        try:
            with open(os.path.expanduser(args.keydicts_json)) as keyfile:
                keys = json.load(keyfile)
            #end with
        except Exception:
            error = 'ERROR, could not locate file with key dicts for portal auth --keydicts-json\n'
            sys.exit(error)
        #end try
        ff_key = keys.get(args.ff_env)
    #end if

    # Check args
    if not ff_key:
        error = 'ERROR, missing key for {0} environment in key dicts for auth\n'.format(args.ff_env)
        sys.exit(error)
    #end if

    if not args.cwl_bucket:
        if args.post_workflow or args.post_cwl:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow requires --cwl-bucket argument\n'
            sys.exit(error)
        #end if
    #end if

    if not args.account:
        if args.post_workflow or args.post_cwl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow | --post-ecr requires --account argument\n'
            sys.exit(error)
        #end if
    #end if

    if not args.region:
        if args.post_workflow or args.post_cwl or args.post_ecr:
            error = 'MISSING ARGUMENT, --post-cwl | --post-workflow | --post-ecr requires --region argument\n'
            sys.exit(error)
        #end if
    #end if

    if not args.project_uuid:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --project-uuid argument\n'
            sys.exit(error)
        #end if
    #end if

    if not args.institution_uuid:
        if args.post_software or args.post_file_format or args.post_file_reference or args.post_workflow or args.post_metaworkflow:
            error = 'MISSING ARGUMENT, --post-software | --post-file-format | --post-file-reference |  --post-workflow | --post-workflow requires --institution-uuid argument\n'
            sys.exit(error)
        #end if
    #end if

    # Run patching for repo
    for repo in args.repos:
        _post_patch_repo(ff_key, repo, args.cwl_bucket, args.account, args.region,
                         args.project_uuid, args.institution_uuid,
                         args.post_software, args.post_file_format, args.post_file_reference,
                         args.post_workflow, args.post_metaworkflow,
                         args.post_cwl, args.post_ecr, args.del_prev_version)
    #end for

#end def


#################################################################
#
#    MAIN
#
#################################################################
if __name__ == "__main__":

    main()

#end if
