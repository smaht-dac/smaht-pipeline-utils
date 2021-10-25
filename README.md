# cgap-pipeline-utils

Collection of utilities for cgap-pipeline

#### deploy_pipeline

    usage: pipeline_utils deploy_pipeline [-h] --ff-env FF_ENV --repos REPOS
                                      [REPOS ...]
                                      [--keydicts-json KEYDICTS_JSON]
                                      [--cwl-bucket CWL_BUCKET]
                                      [--account ACCOUNT] [--region REGION]
                                      [--project-uuid PROJECT_UUID]
                                      [--institution-uuid INSTITUTION_UUID]
                                      [--post-software] [--post-file-format]
                                      [--post-file-reference]
                                      [--post-workflow] [--post-metaworkflow]
                                      [--post-cwl] [--post-ecr]
                                      [--del-prev-version]

    Utility to automatically deploy a pipeline

    optional arguments:
    -h, --help            show this help message and exit
    --ff-env FF_ENV       environment to use for deployment
    --repos REPOS [REPOS ...]
                        list of repos to deploy, must follow expected
                        structure (see docs)
    --keydicts-json KEYDICTS_JSON
                        path to file with key dicts for portal auth in json
                        format
    --cwl-bucket CWL_BUCKET
                        cwl-bucket to use for deployment
    --account ACCOUNT     account to use for deployment
    --region REGION       region to use for deployment
    --project-uuid PROJECT_UUID
                        uuid for project to use for deployment
    --institution-uuid INSTITUTION_UUID
                        uuid for institution to use for deployment
    --post-software       post | patch Software objects
    --post-file-format    post | patch FileFormat objects
    --post-file-reference
                        post | patch FileReference objects
    --post-workflow       post | patch Workflow objects
    --post-metaworkflow   post | patch MetaWorkflow objects
    --post-cwl            upload cwl files
    --post-ecr            create docker images and push to ECR
    --del-prev-version
