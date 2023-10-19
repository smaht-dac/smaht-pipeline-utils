====================
smaht_pipeline_utils
====================

This is the entry point for a collection of utilities available as commands:

  - :ref:`pipeline_deploy <pipeline_deploy>`

Usage:

.. code-block:: bash

    smaht_pipeline_utils [COMMAND] [ARGS]

.. _pipeline_deploy:

pipeline_deploy
+++++++++++++++

Utility to automatically deploy pipeline's components from a target repository.
It is possible to specify multiple target repositories to deploy multiple pipelines at the same time.

Usage:

.. code-block:: bash

    smaht_pipeline_utils pipeline_deploy --ff-env FF_ENV --repos REPO [REPO ...] [OPTIONAL ARGS]

**Arguments:**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Argument
     - Definition
   * - *-\-ff-env*
     - Environment to use for deployment
   * - *-\-repos*
     - List of directories for the repositories to deploy, each repository must follow the expected structure (see :ref:`docs <repo>`)

**Optional Arguments:**

.. list-table::
  :widths: 25 75
  :header-rows: 1

  * - Argument
    - Definition
  * - *-\-builder*
    - Builder to use to deploy Docker containers to AWS ECR through AWS CodeBuild [<ff-env>-pipeline-builder]
  * - *-\-branch*
    - Branch to use to deploy Docker containers to AWS ECR through AWS CodeBuild [main]
  * - *-\-local-build*
    - Trigger a local build for Docker containers instead of using AWS CodeBuild
  * - *-\-keydicts-json*
    - Path to file with keys for portal auth in JSON format [~/.cgap-keys.json]
  * - *-\-wfl-bucket*
    - Bucket to use for upload of Workflow Description files (CWL or WDL)
  * - *-\-account*
    - AWS account to use for deployment
  * - *-\-region*
    - AWS account region to use for deployment
  * - *-\-project*
    - Project to use for deployment [cgap-core]
  * - *-\-institution*
    - Institution to use for deployment [hms-dbmi]
  * - *-\-post-software*
    - DEPLOY | UPDATE Software objects (.yaml or .yml)
  * - *-\-post-file-format*
    - DEPLOY | UPDATE File Format objects (.yaml or .yml)
  * - *-\-post-file-reference*
    - DEPLOY | UPDATE File Reference objects (.yaml or .yml)
  * - *-\-post-workflow*
    - DEPLOY | UPDATE Workflow objects (.yaml or .yml)
  * - *-\-post-metaworkflow*
    - DEPLOY | UPDATE Pipeline objects (.yaml or .yml)
  * - *-\-post-wfl*
    - Upload Workflow Description files (.cwl or .wdl)
  * - *-\-post-ecr*
    - Build Docker container images and push to AWS ECR.
      By default will use AWS CodeBuild unless *-\-local-build* flag is set
  * - *-\-debug*
    - Turn off DEPLOY | UPDATE action
  * - *-\-verbose*
    - Print the JSON structure created for the objects
  * - *-\-validate*
    - Validate YAML objects against schemas. Turn off DEPLOY | UPDATE action
  * - *-\-sentieon-server*
    - Address for Sentieon license server
  * -
    -
