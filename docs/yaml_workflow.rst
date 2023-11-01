.. _workflow:

========
Workflow
========

This documentation provides a comprehensive guide to the template structure necessary for implementing *Workflow* objects.
These objects enable users to codify pipeline steps and store metadata to track inputs, outputs, software,
and description files (e.g., WDL or CWL) for each workflow.

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
      language: <language>                # cwl, wdl
      main: <file>                        # .cwl or .wdl file
      child:
        - <file>                          # .cwl or .wdl file

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
        argument_type: qc
        argument_to_be_attached_to: <file_output_name>
        # Fields to specify the output type
        #   either json or zipped folder
        json: <boolean>
        zipped: <boolean>

      # Report output
      <report_output_name>:
        argument_type: report


General Fields Definition
+++++++++++++++++++++++++

Required
^^^^^^^^
All the following fields are required.

name
----
Name of the workflow, **MUST BE GLOBALLY UNIQUE (ACROSS THE PORTAL OBJECTS)**.

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

At the moment we support two standards, `Common Workflow Language <https://www.commonwl.org>`__ (CWL) and `Workflow Description Language <https://openwdl.org>`__ (WDL).

input
-----
Description of input files and parameters for the workflow. See :ref:`Input Definition <input_a>`.

output
------
Description of expected outputs for the workflow. See :ref:`Output Definition <output_a>`.

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


.. _input_a:

Input Definition
++++++++++++++++
Each argument is defined by its name. Additional subfields need to be specified depending on the argument type.

argument_type
^^^^^^^^^^^^^
Definition of the type of the argument.

For a **file** argument, the argument type is defined as ``file.<format>``, where ``<format>`` is the format used by the file.
``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

For a **parameter** argument, the argument type is defined as ``parameter.<type>``, where ``<type>`` is the type of the value expected for the argument [string, integer, float, json, boolean].


.. _output_a:

Output Definition
+++++++++++++++++
Each output is defined by its name. Additional subfields need to be specified depending on the output type.

argument_type
^^^^^^^^^^^^^
Definition of the type of the output.

For a **file** output, the argument type is defined as ``file.<format>``, where ``<format>`` is the format used by the file.
``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

For a **report** output, the argument type is defined as ``report``.

For a **QC** (Quality Control) output, the argument type is defined as ``qc``.

For a QC, it is possible to generate two different types of output: a key-value pairs JSON file and a compressed file.
The JSON file can be used to create a summary report of the quality metrics generated by the QC process.
The compressed file can be used to store the original output for the QC, including additional data or graphs.
Both the JSON file and compressed file will be attached to the file specified as target by ``argument_to_be_attached_to`` with a ``QualityMetric`` object.
The content of the JSON file will be patched directly on the object, while the compressed file will be made available for download via a link.
The output type can be specified by setting ``json: True`` or ``zipped: True`` in the the QC output definition.

Template for key-value pairs JSON:

.. code-block:: python

  }
    "name": "Quality metric name",
    "qc_values": [
      {
        "key": "Name of the key",
        "tooltip": "Tooltip for the key",
        "value": "Value for the key"
      }
    ]
  }

secondary_files
^^^^^^^^^^^^^^^
This field can be used for output **files**.

List of ``<format>`` for secondary files associated to the output file.
Each ``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

argument_to_be_attached_to
^^^^^^^^^^^^^^^^^^^^^^^^^^
This field can be used for output **QCs**.

Name of the output file the QC is calculated for.
