.. _deploy_pipeline:

======================================
Deploy Pipelines to a CGAP Environment
======================================

This document describes how to deploy pipelines to a target CGAP environment.
Although it's possible to run the deployment from a local machine, we highly recommend using an EC2 machine.

Setup an EC2 Machine
====================

This step may be skipped if you have an EC2 already set up.

We recommend using the following configuration:

  * AMI: Use a linux distribution (64-bit, x86)
  * Instance Type: t3.large or higher
  * Storage: 50+GB in main volume

Install Docker
==============

The deployment code will try to trigger remote codebuild jobs to build and push the Docker containers implemented for the pipelines directly in AWS.
However, if no builder has been setup and it's available, it is possible to run a local build using Docker by passing the flag ``--local-build`` to the deployment command.

Running a local build requires having a Docker application running on the machine.
To install Docker in a EC2 machine, refer to the following instructions based on an Amazon Linux AMI:

Update packages: ``sudo yum update -y``

Install the Docker Engine package:
``sudo yum install docker``

Start the docker service:
``sudo service docker start``

Ensure Docker is installed correctly and has the proper permissions
by running a test command:
``docker run hello-world``

More information on how to setup Docker can be found in the
`AWS Documentation <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html>`_.

We now need to install the ``pipeline_utils`` software to deploy the pipeline components.

Install pipeline_utils
======================

The software is python based.
To install the software and the required packages it is recommended to
use a fresh virtual environment running Python 3.7 or 3.8.

We recommend using pyenv to manage virtual environments.
Instructions for installing and using
pyenv can be found `here <https://realpython.com/intro-to-pyenv/>`_.

Once the virtual environment is set up and activated, we can proceed to :ref:`install <install>` cgap-pipeline-utils software.

.. code-block:: bash

  # Install from source
  git clone https://github.com/dbmi-bgm/cgap-pipeline-utils.git
  cd cgap-pipeline-utils
  make configure
  make update
  make build
  cd ..

  # Install from pypi
  pip install cgap-pipeline-utils

To check that the software is correctly installed, try to run ``pipeline_utils``.
If this fail with a bash "command not found" error, try ``poetry run pipeline_utils`` instead.

Set Up Credentials and Environmental Variables
==============================================

AWS Auth Credentials
--------------------

To deploy pipelines components in a specific AWS account,
we need to setup the following environmental variables to authenticate to the account.

.. code-block:: bash

  export AWS_ACCOUNT_NUMBER=
  export TIBANNA_AWS_REGION=
  export GLOBAL_ENV_BUCKET=
  export S3_ENCRYPT_KEY=

  export AWS_ACCESS_KEY_ID=
  export AWS_SECRET_ACCESS_KEY=

  # Optional, depending on the account
  export S3_ENCRYPT_KEY_ID=
  export AWS_SESSION_TOKEN=

**Tips**:

* *GLOBAL_ENV_BUCKET* can be found in AWS S3. After logging into the AWS
  console and navigating to the S3 page, this variable is the name of the bucket that ends in "-envs".
* *S3_ENCRYPT_KEY* and *S3_ENCRYPT_KEY_ID* can be found in the AWS Secrets Manager.
* *AWS_SESSION_TOKEN* is used by some single sign-on platforms for managing
  credentials but may not be required otherwise.
* *TIBANNA_AWS_REGION* is the region for the AWS account.

Portal Credentials
------------------

We also need to setup credentials to authenticate to the portal database to push some of the portal components.
These credentials need to be stored as a keypair file as described
`here <https://github.com/dbmi-bgm/cgap-portal/blob/master/docs/public/help/access_keys.md>`_.

The default path used by the code to locate this file is ``~/.cgap-keys.json``.
However, it is possible to specify a different keypair file throug the command line, if desired.

Target Account Information
--------------------------

Finally we need to setup the information to identify the target environment to use for the deployment.

.. code-block:: bash

  # Set the name of the target environment
  #   e.g., cgap-wolf
  export ENV_NAME=

  # Set the bucket used to store the worklow description files
  #   e.g., cgap-biotest-main-application-tibanna-cwls
  export WFL_BUCKET=

  # Set the path to the keypair file with the portal credential
  #   e.g., /.cgap-keys.json
  export KEYDICTS_JSON=

  # Set up project and institution
  #   Project and institution need to correspond to metadata present on the portal
  #   e.g., cgap-core and hms-dbmi
  export PROJECT=
  export INSTITUTION=

  # If running sentieon code,
  #   specify the address for the server that validate the software license
  #   e.g., 0.0.0.0
  export SENTIEON_LICENSE=

**Tips:**

* *ENV_NAME* can be found in the portal health page under ``Namespace``.
* *WFL_BUCKET* can be found in the portal health page under ``Tibanna CWLs Bucket``.

Running the Deployment
======================

The following code will use ``pipeline_deploy`` command to deploy all the components from the repositories specified
by the ``--repos`` argument.

.. code-block:: bash

  pipeline_utils pipeline_deploy \
    --ff-env ${ENV_NAME} \
    --keydicts-json ${KEYDICTS_JSON} \
    --wfl-bucket ${WFL_BUCKET} \
    --account ${AWS_ACCOUNT_NUMBER} \
    --region ${TIBANNA_AWS_REGION} \
    --project ${PROJECT} \
    --institution ${INSTITUTION} \
    --sentieon-server ${SENTIEON_LICENSE} \
    --post-software \
    --post-file-format \
    --post-file-reference \
    --post-workflow \
    --post-metaworkflow \
    --post-wfl \
    --post-ecr \
    --repos REPO [REPO ...]

It is possible to add flags to run the command in various debug modes, to validate the objects and test the pipeline implementation without running a real deployment.
For more details on the command line arguments refer to the documentation for the :ref:`pipeline_deploy <pipeline_deploy>` command.

An important argument is ``--branch``, this argument specifies the branch to check out for cgap-pipeline-main to build ECR through codebuild.
The default is set to the main branch. The ``--local-build`` flag will prevent the code to try using codebuild and force a local build using Docker instead.

*Note: we are working to enable more builder and a selection with a command line argument for which builder to use to deploy modules from different repositories through codebuild.*

Deploying CGAP Pipelines
========================

CGAP pipelines are released as a complete package with a customized set up for automated deployment to the desired environment.
To deploy the pipelines run the following steps:

1. Clone the main pipeline repository.
The submodules will be empty and set to the current commits saved for the main branch.

.. code-block:: bash

  git clone https://github.com/dbmi-bgm/cgap-pipeline-main.git

2. Check out the desired version.
This will set the submodules to the commits saved for that pipeline release.

.. code-block:: bash

  git checkout <version>

3. Download the content for each submodule.
The submodules will be set in detached state on their current commit.

.. code-block:: bash

  make pull

4. Build pipeline_utils (optional).
This will build from source the latest version linked for the current release.

.. code-block:: bash

  make configure
  make update
  make build

5. Set up the auth credentials as described above.

6. Set the target account information in the ``.env`` file.

7. Test the deployment using the base module only.

.. code-block:: bash

  make deploy-base

8. Deploy all the other modules.

.. code-block:: bash

  makde deploy-all

Troubleshooting
===============

Some possible errors are described below.

Auth Errors
-----------

.. code-block:: bash

  botocore.exceptions.ClientError: An error occurred (400) when calling
  the HeadBucket operation: Bad Request

This may indicate your credentials are out of date. Make sure your AWS
credentials are up to date and source them if necessary.

No Space Left on Device Errors
------------------------------

When running a local build, the EC2 may run out of space.
You can try one of the following:

1. Clean up old docker images that are no longer needed with a
   command such as ``docker rm -v $(docker ps -aq -f 'status=exited')``.
   More details at `<https://vsupalov.com/cleaning-up-after-docker/>`_.
2. Increase the size of your primary EBS volume: details
   `here <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/requesting-ebs-volume-modifications.html>`_.
3. Mount another EBS volume to ``/var/lib/docker``. Instructions to
   format and mount a volume are described
   `here <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html>`_,
   but note that you would skip the `mkdir` step and mount the
   volume to ``/var/lib/docker``.
