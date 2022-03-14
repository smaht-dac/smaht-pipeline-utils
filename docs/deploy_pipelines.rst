=============================================
Deploying Pipelines to a New CGAP Environment
=============================================

This document describes how to deploy CGAP pipelines. Using an EC2 is
recommended; trying to deploy from a local MacOS may work for some
pipelines but fail for others.

Setting up an EC2
+++++++++++++++++

Launch EC2
==========

This step may be skipped if you have an EC2 already.

If not configured properly, building the docker images may be slow or
the EC2 may run out of space.

* AMI: Use a linux distribution (64-bit, x86)
* Instance Type: t3.large or higher
* Storage: 32GB in main volume

Install Docker
==============

If Docker isn't already on the EC2, it will need to be installed **(skip
  this step if Docker is already installed and running)**. The
following instructions are based on an Amazon Linux AMI, but more
instructions can be found in the
`AWS Documentation <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html>`_.

Update packages: ``sudo yum update -y``

Install the Docker Engine package:
``sudo yum install docker``

Start the docker service:
``sudo service docker start``

Ensure Docker is installed correctly and has the proper permissions
by running a test command:
``docker run hello-world``


Installing packages
===================

For the CGAP python packages, it is best to use a fresh virtual
environment, running Python 3.6.10. We recommend using pyenv to
manage virtual environments. Instructions for installing and using
pyenv can be found `here <https://realpython.com/intro-to-pyenv/>`_.

Once inside the virtual environment, we need to install
cgap-pipeline-utils v1.6.0:

.. code-block:: bash

  git clone https://github.com/dbmi-bgm/cgap-pipeline-utils.git
  cd cgap-pipeline-utils
  pip install --upgrade pip
  pip install poetry
  poetry install
  cd ..


To check that it is installed correctly, make sure that you can run
``pipeline_utils``. If you get a bash "command not found" error, try
using ``poetry run pipeline_utils`` instead. If this doesn't work, then
poetry hasn't installed the repo correctly.

After installing the pipeline utils, next we can install
cgap-pipeline-main, v0.0.27:

.. code-block:: bash

  git clone https://github.com/dbmi-bgm/cgap-pipeline-main.git
  cd cgap-pipeline-main

  # checkout the desired version
  git checkout v0.0.27

  # populate the submodules
  make pull

Set Up Credentials
==================

Environmental Variables
-----------------------

The following environmental variables are needed:

.. code-block:: bash

  export AWS_ACCOUNT_NUMBER=
  export TIBANNA_AWS_REGION=
  export GLOBAL_BUCKET_ENV=
  export S3_ENCRYPT_KEY=

  # these 3 from Okta (refresh every 4 hours or so)
  export AWS_ACCESS_KEY_ID=
  export AWS_SECRET_ACCESS_KEY=
  export AWS_SESSION_TOKEN=

* **AWS_ACCOUNT_NUMBER** can usually be found
  `here <https://hms-dbmi.atlassian.net/wiki/spaces/FOURDNDCIC/pages/851083341/Deployment+Environments>`_.
* **TIBANNA_AWS_REGION** is always ``us-east-1``.
* **S3_ENCRYPT_KEY** most developers have already; if you
  need this, contact the back-end team to send it to you securely.
* **GLOBAL_BUCKET_ENV** can be found in S3. If you log into the AWS
  console and go to S3, this variable is the name of the bucket that ends
  in "-envs".

The last 3 variables can be obtained by logging into Okta, clicking on
the account of interest, and clicking "Command line or programmatic
access". You can click under "Option 1" to copy them.

These variables can be stored in a file using the template above (with
the export commands) so that they can be sourced when needed. The
last 3 regularly reset and need to be regenerated often. Run `source`
on this file before running the ``pipeline_utils`` commands.


Portal Credentials
------------------

Make sure the file that stores your access keys is present on the EC2.
The default location the code looks for is ``~/.cgap-keydicts.json``.
However, you can also specify a keypair file at a different location
if desired (such as ``~/.cgap-keys.json`` as used for SubmitCGAP).
Instructions for creating access keys for CGAP can be found
`here <https://github.com/dbmi-bgm/cgap-portal/blob/master/docs/public/help/access_keys.md>`_.

Running Commands
================

The basic command to deploy the pipelines is the following:

.. code-block:: bash

  pipeline_utils deploy_pipeline --ff-env <env-name> --repos \
    cgap-pipeline-base cgap-pipeline-upstream-GATK \
    cgap-pipeline-upstream-sentieon cgap-pipeline-SNV-germline \
    cgap-pipeline-SV-germline --account $AWS_ACCOUNT_NUMBER \
    --region $TIBANNA_AWS_REGION --cwl-bucket <bucket-name> \
    --post-software --post-file-format --post-file-reference \
    --post-workflow --post-metaworkflow --post-cwl --post-ecr \
    --del-prev-version

**Tips and Options:**

* the ``--ff-env`` parameter value is found at the
  health page under the ``Namespace`` field
* the ``--cwl-bucket`` parameter value is found at the health page
  under the ``Tibanna CWLs Bucket`` field
* use ``--keydicts-json <keyfile>`` if your access keys aren't stored at
  ``~/.cgap-keydicts.json``
* The above command will attempt to deploy all pipelines; you could
  start with only ``--repos cgap-pipeline-base`` to make sure the
  installation and your credentials are working correctly


Troubleshooting
+++++++++++++++

Some possible errors are described below.

.. code-block:: bash

  botocore.exceptions.ClientError: An error occurred (400) when calling
  the HeadBucket operation: Bad Request

This may indicate your Okta creds are out of date. Regenerate your
credentials as described above and source the file holding them again.


.. code-block:: bash

  executor failed running [/bin/sh -c cpan App::cpanminus &&
  wget https://github.com/ucscGenomeBrowser/kent/archive/v335_base.tar.gz
  &&     tar xzf v335_base.tar.gz &&     export
  KENT_SRC=/usr/local/bin/kent-335_base/src &&     export
  MACHTYPE=$(uname -m) &&     export CFLAGS="-fPIC" &&     export
  MYSQLINC=`mysql_config --include | sed -e 's/^-I//g'` &&
  MYSQLLIBS=`mysql_config --libs` &&     export MYSQLLIBS &&     cd
  $KENT_SRC/lib &&     echo 'CFLAGS="-fPIC"' >
  ../inc/localEnvironment.mk &&     make clean && make &&     cd
  ../jkOwnLib &&     make clean && make &&     cd /usr/local/bin/
  &&     mkdir -p /usr/local/bin/cpanm_bw &&     export
  PERL5LIB=$PERL5LIB:/usr/local/bin/cpanm_bw/lib/perl5 &&
  cpanm -l /usr/local/bin/cpanm_bw Bio::DB::BigFile &&     rm -f
  v335_base.tar.gz &&     rm -rf kent-335_base/ &&     cd
  /usr/local/bin/ensembl-vep &&     perl -Imodules
  t/AnnotationSource_File_BigWig.t &&     cd /usr/local/bin]: exit code: 1
  The push refers to repository
  [586664789363.dkr.ecr.us-east-1.amazonaws.com/snv_germline]
  An image does not exist locally with the tag:
  586664789363.dkr.ecr.us-east-1.amazonaws.com/snv_germline

VEP sometimes has problems building on certain machines, but using an
Amazon EC2 running linux has solved this in the past.

Docker errors
-------------

.. code-block:: bash

  docker: Got permission denied while trying to connect to the Docker
  daemon socket at unix:///var/run/docker.sock: Post
  "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/create": dial
  unix /var/run/docker.sock: connect: permission denied.
  See 'docker run --help'.

If you run into permission errors with Docker, you can try running
``sudo usermod -aG docker $USER`` or using the ``chown`` command to change
ownership of the docker folders.

.. code-block:: bash

  docker: open /var/lib/docker/tmp/GetImageBlob549217035:
  no such file or directory.

This can often be fixed by restarting docker, either with
``sudo systemctl restart docker`` or:

.. code-block:: bash

  sudo service docker stop        
  sudo service docker start


No Space Left on Device errors
------------------------------

If the EC2 runs out of space, you can try one of the following:

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
