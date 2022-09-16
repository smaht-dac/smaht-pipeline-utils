===================
Workflow Definition
===================

.. _workflow:


Template
++++++++

.. code-block:: python

    ## Workflow information #####################################
    #     General information for the workflow
    #############################################################
    # All the following fields are required
    name: <string>
    description: <string>

    runner:
      language: <language>                # CWL, WDL
      main: <file>                        # <workflow_description>.<cwl|wdl>
      child:
        - <file>                          # <workflow_description>.<cwl|wdl>

    # All the following fields are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas
    title: <string>

    software:
      - <software>@<version|commit>

    ## Input information ########################################
    #     Input files and parameters
    #############################################################
    input:

      # File argument
      <file_argument_name>:
        argument_type: file.<format>      # bam, fastq, bwt, ...

      # Parameter argument
      <parameter_argument_name>:
        argument_type: parameter.<type>   # string, integer, float, json, boolean

    ## Output information #######################################
    #     Output files and quality controls
    #############################################################
    output:

      # File output
      <file_output_name>:
        argument_type: file.<format>
        secondary_files:
          - <format>                      # bam, fastq, bwt, ...

      # QC output
      <qc_output_name>:
        argument_type: qc.<type>          # qc_type, e.g. quality_metric_vcfcheck
        argument_to_be_attached_to: <file_output_name>
        # All the following fields are optional and provided as example,
        #   can be expanded to anything accepted by the schema
        html: <boolean>
        json: <boolean>
        table: <boolean>
        zipped: <boolean>
        # If the output is a zipped folder with multiple QC files,
        #   fields to define the target files inside the folder
        html_in_zipped: <file>
        tables_in_zipped:
          - <file>

      # Report output
      <report_output_name>:
        argument_type: report.<type>      # report_type, e.g. file


General Fields Definition
+++++++++++++++++++++++++

Required
^^^^^^^^
All the following fields are required.

name
----
Name of the workflow, **MUST BE GLOBALLY UNIQUE**.

description
-----------
Description of the workflow.

runner
------
Definition of the data processing flow for the workflow.
This field is used to specify the standard language and description files used to define the workflow.
Several subfields need to be specified:

  - **language** [required]: Language standard used for workflow description
  - **main** [required]: Main description file
  - **child** [optional]: List of supplementary description files used by main

*Note*: At the moment we support two standards, `Common Workflow Language <https://www.commonwl.org>`__ (CWL) and `Workflow Description Language <https://openwdl.org>`__ (WDL).

input
-----
Description of input files and parameters for the workflow. See :ref:`Input Definition <input>`.

output
------
Description of expected outputs for the workflow. See :ref:`Output Definition <output>`.

Optional
^^^^^^^^
All the following fields are optional and provided as example. Can be expanded to anything accepted by the schema, see `schemas <https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas>`__.

title
-----
Title of the workflow.

software
--------
List of software used by the workflow.
Each software is specified using the name of the software and the version (either version or commit) in the format ``<software>@<version|commit>``.
Each software needs to match a software that has been previously defined, see :ref:`Software <software>`.


.. _input:

Input Definition
++++++++++++++++
Each argument is defined by its name. Additional subfields need to be specified depending on the argument type.

argument_type
^^^^^^^^^^^^^
Definition of the type of the argument.

For a **file** argument, the argument type is defined as ``file.<format>``, where ``<format>`` is the format used by the file.
``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

For a **parameter** argument, the argument type is defined as ``parameter.<type>``, where ``<type>`` is the type of the value expected for the argument [string, integer, float, json, boolean].


.. _output:

Output Definition
+++++++++++++++++
Each output is defined by its name. Additional subfields need to be specified depending on the output type.

argument_type
^^^^^^^^^^^^^
Definition of the type of the output.

For a **file** output, the argument type is defined as ``file.<format>``, where ``<format>`` is the format used by the file.
``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

For a **QC** (Quality Control) output, the argument type is defined as ``qc.<type>``, where ``<type>`` is a a ``qc_type`` defined in the the schema, see `schemas <https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas>`__.

For a **report** output, the argument type is defined as ``report.<type>``, where ``<type>`` is the type of the report (e.g., file).

*Note*: We are currently re-thinking how QC and report outputs work, the current definitions are temporary solutions that may change soon.

secondary_files
^^^^^^^^^^^^^^^
This field can be used for output **files**.

List of ``<format>`` for secondary files associated to the output file.
Each ``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

argument_to_be_attached_to
^^^^^^^^^^^^^^^^^^^^^^^^^^
This field can be used for output **QCs**.

Name of the output file the QC is calculated for.
