#!/usr/bin/env python3

################################################
#
#   __main__
#     this is the entry point for command line
#
#   Michele Berselli - berselli.michele@gmail.com
#
################################################


import sys, os
import argparse


# Commands
from pipeline_utils import deploy_pipeline_legacy
from pipeline_utils import pipeline_deploy


# Variables
DEPLOY_PIPELINE_LEGACY = 'deploy_pipeline_legacy'
PIPELINE_DEPLOY = 'pipeline_deploy'


def main(args=None):
    '''
        command line wrapper around available commands
    '''
    # Adding parser and subparsers
    parser = argparse.ArgumentParser(prog='pipeline_utils', description='Collection of utilities for cgap-pipeline')
    subparsers = parser.add_subparsers(dest='func', metavar="<command>")

    # Add deploy_pipeline to subparsers, LEGACY
    deploy_pipeline_legacy_parser = subparsers.add_parser(DEPLOY_PIPELINE_LEGACY, description='Utility to automatically deploy a pipeline from a target repository, LEGACY',
                                                help='Utility to automatically deploy a pipeline from a target repository, LEGACY')

    deploy_pipeline_legacy_parser.add_argument('--ff-env', required=True, help='environment to use for deployment')
    deploy_pipeline_legacy_parser.add_argument('--repos', required=True, nargs='+', help='list of repos to deploy, must follow expected structure (see docs)')
    deploy_pipeline_legacy_parser.add_argument('--keydicts-json', required=False, help='path to file with key dicts for portal auth in JSON format',
                                                           default='~/.cgap-keydicts.json')
    deploy_pipeline_legacy_parser.add_argument('--cwl-bucket', required=False, help='cwl-bucket to use for deployment')
    deploy_pipeline_legacy_parser.add_argument('--account', required=False, help='account to use for deployment')
    deploy_pipeline_legacy_parser.add_argument('--region', required=False, help='region to use for deployment')
    deploy_pipeline_legacy_parser.add_argument('--project-uuid', required=False, help='uuid for project to use for deployment',
                                                          default='12a92962-8265-4fc0-b2f8-cf14f05db58b')
    deploy_pipeline_legacy_parser.add_argument('--institution-uuid', required=False, help='uuid for institution to use for deployment',
                                                              default='828cd4fe-ebb0-4b36-a94a-d2e3a36cc989')

    deploy_pipeline_legacy_parser.add_argument('--post-software', action='store_true', help='post | patch Software objects')
    deploy_pipeline_legacy_parser.add_argument('--post-file-format', action='store_true', help='post | patch FileFormat objects')
    deploy_pipeline_legacy_parser.add_argument('--post-file-reference', action='store_true', help='post | patch FileReference objects')
    deploy_pipeline_legacy_parser.add_argument('--post-workflow', action='store_true', help='post | patch Workflow objects')
    deploy_pipeline_legacy_parser.add_argument('--post-metaworkflow', action='store_true', help='post | patch MetaWorkflow objects')
    deploy_pipeline_legacy_parser.add_argument('--post-cwl', action='store_true', help='upload cwl files')
    deploy_pipeline_legacy_parser.add_argument('--post-ecr', action='store_true', help='create docker images and push to ECR')
    deploy_pipeline_legacy_parser.add_argument('--del-prev-version', action='store_true')

    # cgap-specific
    deploy_pipeline_legacy_parser.add_argument('--sentieon-server', required=False, help='address for sentieon license server',
                                                             default='0.0.0.0:0')

    # Add pipeline_deploy to subparsers
    pipeline_deploy_parser = subparsers.add_parser(PIPELINE_DEPLOY, description='Utility to automatically deploy pipeline components from a target repository',
                                                    help='Utility to automatically deploy pipeline components from a target repository')

    pipeline_deploy_parser.add_argument('--ff-env', required=True, help='Environment to use for deployment')
    pipeline_deploy_parser.add_argument('--repos', required=True, nargs='+', help='List of repos to deploy, must follow expected structure (see docs)')
    pipeline_deploy_parser.add_argument('--keydicts-json', required=False, help='Path to file with key dicts for portal auth in JSON format (see docs)',
                                                           default='~/.cgap-keydicts.json')
    pipeline_deploy_parser.add_argument('--wfl-bucket', required=False, help='Bucket to use for deployment of Workflow Description files')
    pipeline_deploy_parser.add_argument('--account', required=False, help='Account to use for deployment')
    pipeline_deploy_parser.add_argument('--region', required=False, help='Region to use for deployment')
    pipeline_deploy_parser.add_argument('--project', required=False, help='Project to use for deployment',
                                                          default='cgap-core')
    pipeline_deploy_parser.add_argument('--institution', required=False, help='Institution to use for deployment',
                                                              default='hms-dbmi')

    pipeline_deploy_parser.add_argument('--post-software', action='store_true', help='POST|PATCH Software objects')
    pipeline_deploy_parser.add_argument('--post-file-format', action='store_true', help='POST|PATCH FileFormat objects')
    pipeline_deploy_parser.add_argument('--post-file-reference', action='store_true', help='POST|PATCH FileReference objects')
    pipeline_deploy_parser.add_argument('--post-workflow', action='store_true', help='POST|PATCH Workflow objects')
    pipeline_deploy_parser.add_argument('--post-metaworkflow', action='store_true', help='POST|PATCH MetaWorkflow objects')
    pipeline_deploy_parser.add_argument('--post-wfl', action='store_true', help='Upload Workflow Description files (.cwl, .wdl)')
    pipeline_deploy_parser.add_argument('--post-ecr', action='store_true', help='Build Docker images and push to ECR')

    pipeline_deploy_parser.add_argument('--debug', action='store_true', help='Turn off POST|PATCH action')
    pipeline_deploy_parser.add_argument('--verbose', action='store_true', help='Print the JSON structure created for objects')

    pipeline_deploy_parser.add_argument('--validate', action='store_true', help='Validate YAML object against schemas. Turn off POST|PATCH action and ignore --verbose and --debug flags')

    # cgap-specific
    pipeline_deploy_parser.add_argument('--sentieon-server', required=False, help='Address for Sentieon license server',
                                                             default='0.0.0.0:0')

    # Subparsers map
    subparser_map = {
                    DEPLOY_PIPELINE_LEGACY: deploy_pipeline_legacy_parser, # LEGACY
                    PIPELINE_DEPLOY: pipeline_deploy_parser
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
    args = parser.parse_args()

    # Call the right tool
    if args.func == DEPLOY_PIPELINE_LEGACY:
        deploy_pipeline_legacy.main(args)
    elif args.func == PIPELINE_DEPLOY:
        pipeline_deploy.main(args)


if __name__ == "__main__":
    main()
