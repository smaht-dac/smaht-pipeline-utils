#!/usr/bin/env python3

################################################
#
#   __main__
#     this is the entry point for command line
#
#   Michele Berselli - berselli.michele@gmail.com
#   Phil Grayson - phil.d.grayson@gmail.com
#
################################################

################################################
#   Libraries
################################################
import sys, os
import argparse

# Commands
from pipeline_utils import deploy_pipeline

################################################
#   Functions
################################################
################################################
#   main
################################################
def main(args=None):
    '''
        command line wrapper around available commands
    '''
    # Adding parser and subparsers
    parser = argparse.ArgumentParser(prog='pipeline_utils', description='Collection of utilities for cgap-pipeline')
    subparsers = parser.add_subparsers(dest='func', metavar="<command>")

    # Add deploy_pipeline to subparsers
    deploy_pipeline_parser = subparsers.add_parser('deploy_pipeline', description='Utility to automatically deploy a pipeline',
                                                help='Utility to automatically deploy a pipeline')

    deploy_pipeline_parser.add_argument('--ff-env', required=True, help='environment to use for deployment')
    deploy_pipeline_parser.add_argument('--repos', required=True, nargs='+', help='list of repos to deploy, must follow expected structure (see docs)')
    deploy_pipeline_parser.add_argument('--keydicts-json', required=False, help='path to file with key dicts for portal auth in json format',
                                                           default='~/.cgap-keydicts.json')
    deploy_pipeline_parser.add_argument('--cwl-bucket', required=False, help='cwl-bucket to use for deployment')
    deploy_pipeline_parser.add_argument('--account', required=False, help='account to use for deployment')
    deploy_pipeline_parser.add_argument('--region', required=False, help='region to use for deployment')
    deploy_pipeline_parser.add_argument('--project-uuid', required=False, help='uuid for project to use for deployment',
                                                          default='12a92962-8265-4fc0-b2f8-cf14f05db58b')
    deploy_pipeline_parser.add_argument('--institution-uuid', required=False, help='uuid for institution to use for deployment',
                                                              default='828cd4fe-ebb0-4b36-a94a-d2e3a36cc989')

    deploy_pipeline_parser.add_argument('--post-software', action='store_true', help='post | patch Software objects')
    deploy_pipeline_parser.add_argument('--post-file-format', action='store_true', help='post | patch FileFormat objects')
    deploy_pipeline_parser.add_argument('--post-file-reference', action='store_true', help='post | patch FileReference objects')
    deploy_pipeline_parser.add_argument('--post-workflow', action='store_true', help='post | patch Workflow objects')
    deploy_pipeline_parser.add_argument('--post-metaworkflow', action='store_true', help='post | patch MetaWorkflow objects')
    deploy_pipeline_parser.add_argument('--post-cwl', action='store_true', help='upload cwl files')
    deploy_pipeline_parser.add_argument('--post-ecr', action='store_true', help='create docker images and push to ECR')
    deploy_pipeline_parser.add_argument('--del-prev-version', action='store_true')

    # Subparsers map
    subparser_map = {
                    'deploy_pipeline': deploy_pipeline_parser
                    }

    # Checking arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif len(sys.argv) == 2:
        if sys.argv[1] in subparser_map:
            subparser_map[sys.argv[1]].print_help(sys.stderr)
            sys.exit(1)
        else:
            parser.print_help(sys.stderr)
            sys.exit(1)
        #end if
    #end if
    args = parser.parse_args()

    # Call the right tool
    if args.func == 'deploy_pipeline':
        deploy_pipeline.main(args)
    #end if

#################################################################
#
#    MAIN
#
#################################################################
if __name__ == "__main__":

    main()

#end if
