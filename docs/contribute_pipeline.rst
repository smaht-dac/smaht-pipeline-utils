.. _contribute_pipeline:

======================
Contribute a Pipeline
======================

Welcome to the documentation on how to contribute pipelines.

We're glad that you're interested in contributing a pipeline, and we appreciate your help in expanding and improving our offering.
This document will guide you through the process of building and deploying a new pipeline in the portal infrastructure.


Building a Pipeline
^^^^^^^^^^^^^^^^^^^

A pipeline requires several components to be compatible and run within our infrastructure:

- Workflow description files
- Docker containers
- Portal objects
- A name and a version for the pipeline

These components need to be organized following a validated structure to enable automated deployment.
More information on this specific structure is available :ref:`here <repo>`.

Although it's not strictly necessary, it is highly recommended to set up a GitHub repository to store and organize all the components.


Workflow Description Files
--------------------------

Workflow description languages are standards for describing data analysis pipelines that are portable across different platforms.

Each step of the pipeline that needs to execute in a single computing environment must be defined in a corresponding workflow description file using one of the supported languages.
At the moment we are supporting two standards, `Common Workflow Language <https://www.commonwl.org>`__ (CWL) and `Workflow Description Language <https://openwdl.org>`__ (WDL), and we are working to add support for more standards (e.g., Snakemake).

Each step codified as a workflow description file will execute on a single EC2 machine through our executioner software, `Tibanna <https://github.com/4dn-dcic/tibanna>`__.

*Note: the workflow description file must have a .wdl or .cwl extension to be recognized during the automated deployment.*

The following example implement the steps ``foo`` and ``bar`` for the ``foo_bar`` pipeline.
Each step will execute independently on a single EC2 machine.

::

  pipeline-foo_bar
  │
  ├── descriptions
  │   ├── foo.cwl
  │   └── bar.wdl
  ..

Typically, when creating a workflow description file, the code will make reference to a Docker container.
To store these containers, we use private ECR repositories that are specific to each AWS account.
To ensure that the description file points to the appropriate image, we utilize two placeholders, **VERSION** and **ACCOUNT**,
which will be automatically substituted in the file with the relevant account information during deployment.
If the code runs Sentieon software and requires the *SENTIEON_LICENSE* environmental variable to be set,
the **LICENSEID** placeholder will be substituted by the code with the server address provided to the :ref:`deploy command <pipeline_deploy>`.

Example of a CWL code with the placeholders

.. code-block:: yaml

  #!/usr/bin/env cwl-runner

  cwlVersion: v1.0

  class: CommandLineTool

  requirements:
    - class: EnvVarRequirement
      envDef:
        -
          envName: SENTIEON_LICENSE
          envValue: LICENSEID

  hints:
    - class: DockerRequirement
      dockerPull: ACCOUNT/upstream_sentieon:VERSION

  baseCommand: [sentieon, driver]

  ...

Docker Containers
-----------------

As we are using temporary EC2 machines, all code to be executed must be packaged and distributed in Docker containers.

Each pipeline can have multiple containers, and each container requires its own directory with all the related components and the corresponding *Dockerfile*.

During the automated deployment, each image will be automatically built, tagged based on the name of the directory, and pushed to the corresponding ECR repository within AWS.
More information on the deployment process :ref:`here <deploy_pipeline>`.

The following example will build the images ``image_foo`` and ``image_bar``, and push them to ECR during the deployment.

::

  pipeline-foo_bar
  │
  ├── dockerfiles
  │   │
  │   ├── image_foo
  │   │   ├── foo.sh
  │   │   └── Dockerfile
  │   │
  │   └── image_bar
  │       ├── bar.py
  │       └── Dockerfile
  ..


Portal Objects
--------------

Workflow description files and Docker containers are necessary to execute the code and run each step of the pipeline in isolation.
However, a pipeline is a complex object that consists of multiple steps chained together.

To create these dependencies and specify the necessary details for the execution of each individual workflow and the end-to-end processing of the pipeline, we need additional supporting metadata in the form of YAML objects.
The objects currently available are:

- :ref:`Pipeline <metaworkflow>`,
  this object defines dependencies between workflows, scatter and gather parameters to parallelize execution, reference files and constant input parameters, and EC2 configurations for each of the workflows.
- :ref:`Workflow <workflow>`,
  this object represents a pipeline step and stores metadata to track its inputs, outputs, software, and description files (e.g., WDL or CWL).
- :ref:`Software <software>`,
  this object stores information to track and version a specific software used by the pipeline.
- :ref:`File Reference <file_reference>`,
  this object stores information to track and version a specific reference file used by the pipeline.
- :ref:`File Format <file_format>`,
  this object stores information to represent a file format used by the pipeline.

Please refer to each of the linked pages for details on the schema definitions specific to the object and the available code templates.

*Note: the files defining portal objects must have a .yaml or .yml extension to be recognized during the automated deployment.*

The following example implements workflow objects for the steps ``foo`` and ``bar`` and a pipeline object for the ``foo_bar`` pipeline.
Additional metadata to track reference files, file formats, and software used by the pipeline are also implemented as corresponding YAML objects.

::

  pipeline-foo_bar
  │
  ├── portal_objects
  │   │
  │   ├── workflows
  │   │   ├── foo.yaml
  │   │   └── bar.yaml
  │   │
  │   ├── metaworkflows
  │   │   └── foo_bar.yaml
  │   │
  │   ├── file_format.yaml
  │   ├── file_reference.yaml
  │   └── software.yaml
  ..


PIPELINE and VERSION Files
--------------------------

Finally, automated deployment requires a pipeline version and name. These will also be used to tag some of the components deployed with the pipeline (i.e., Docker containers, workflow description files, Pipeline and Workflow objects).

This information must be provided in separate VERSION and PIPELINE one-line files.

Example

::

  pipeline-foo_bar
  │
  ..
  ├── PIPELINE
  └── VERSION


Examples
--------

Real examples of implemented pipeline modules can be found linked as submodules in our main pipeline repository for the SMaHT project here: https://github.com/smaht-dac/main-pipelines.
