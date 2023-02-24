==============
pipeline_utils
==============

This is the entry point for a collection of utilities available as commands:

  - :ref:`pipeline_deploy <pipeline_deploy>`

Usage:

.. code-block:: bash

    pipeline_utils [COMMAND] [ARGS]

.. _pipeline_deploy:

pipeline_deploy
+++++++++++++++

Utility to automatically deploy pipeline's components from a target repository.
It is possible to specify multiple target repositories to deploy multiple pipelines at the same time.
It is also possible to specify the current repository as a target as ``.``.

Usage:

.. code-block:: bash

    pipeline_utils pipeline_deploy --ff-env FF_ENV --repos REPO [REPO ...] [OPTIONAL ARGS]

**Arguments:**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Argument
     - Definition
   * - *-\-ff-env*
     - Environment to use for deployment
   * - *-\-repos*
     - List of repositories to deploy, must follow expected structure (see :ref:`docs <repo>`)

**Optional Arguments:**

.. list-table::
  :widths: 25 75
  :header-rows: 1

  * - Argument
    - Definition
  * - *-\-branch*
    - Branch to check out for cgap-pipeline-main to build ECR through codebuild [main]
  * - *-\-local-build*
    - Trigger a local ECR build instead of using codebuild
  * - *-\-keydicts-json*
    - Path to file with keys for portal auth in JSON format [~/.cgap-keys.json]
  * - *-\-wfl-bucket*
    - Bucket to use for upload of Workflow Description files (CWL or WDL)
  * - *-\-account*
    - Account to use for deployment
  * - *-\-region*
    - Region to use for deployment
  * - *-\-project*
    - Project to use for deployment [cgap-core]
  * - *-\-institution*
    - Institution to use for deployment [hms-dbmi]
  * - *-\-post-software*
    - POST | PATCH Software objects (.yaml)
  * - *-\-post-file-format*
    - POST | PATCH FileFormat objects (.yaml)
  * - *-\-post-file-reference*
    - POST | PATCH FileReference objects (.yaml)
  * - *-\-post-workflow*
    - POST | PATCH Workflow objects (.yaml)
  * - *-\-post-metaworkflow*
    - POST | PATCH MetaWorkflow objects (.yaml)
  * - *-\-post-wfl*
    - Upload Workflow Description files (.cwl or .wdl)
  * - *-\-post-ecr*
    - Build Docker images and push to ECR.
      By default will try to use codebuild unless *-\-local-build* flag is set
  * - *-\-debug*
    - Turn off POST | PATCH action
  * - *-\-verbose*
    - Print the JSON structure created for the objects
  * - *-\-validate*
    - Validate YAML objects against schemas (turn off POST | PATCH)
  * - *-\-sentieon-server*
    - Address for Sentieon license server
  * -
    -
