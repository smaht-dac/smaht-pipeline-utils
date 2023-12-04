.. _metaworkflow:

========
Pipeline
========

This documentation provides a comprehensive guide to the template structure necessary for implementing *Pipeline* objects.
These objects enable users to define workflow dependencies, parallelize execution by defining scattering and gathering parameters,
specify reference files and constant input parameters, and configure AWS EC2 instances for executing each workflow within the pipeline.

Template
++++++++

.. code-block:: python

    ## Pipeline information #####################################
    #     General information for the pipeline
    #############################################################
    # All the following fields are required
    name: <string>
    description: <string>

    category:
      - <category>                          # Alignment, ...

    ## General arguments ########################################
    #     Pipeline input, reference files, and general arguments
    #       define all arguments for the pipeline here
    #############################################################
    input:

      # File argument
      <file_argument_name>:
        argument_type: file.<format>        # bam, fastq, bwt, ...
        # All the following fields are optional and provided as example,
        #   can be expanded to anything accepted by the schema
        dimensionality: <integer>
        files:
          - <file_name>@<version>

      # Parameter argument
      <parameter_argument_name>:
        argument_type: parameter.<type>     # string, integer, float, array, object, boolean
        # All the following fields are optional and provided as example,
        #   can be expanded to anything accepted by the schema
        value: <...>

    ## Workflows and dependencies ###############################
    #     Information for the workflows and their dependencies
    #############################################################
    workflows:

      ## Workflow definition #####################
      ############################################
      <workflow_name>[@<tag>]:

        ## Hard dependencies ###############
        #   Dependencies that must complete
        ####################################
        dependencies:
          - <workflow_name>[@<tag>]

        ## Fixed shards ####################
        #   Allows to force a fixed shards structure ignoring
        #     the input structure, scatter and gather dimensions
        ####################################
        shards: [[<string>], ..]             # e.g., [['0'], ['1'], ['2']]

        ## Lock version ####################
        #   Specific version to use
        #     for the workflow
        ####################################
        version: <string>

        ## Specific arguments ##############
        #   General arguments that need to be referenced and
        #     specific arguments for the workflow:
        #       - file arguments that need to source the output from a previous step
        #       - file arguments that need to scatter or gather
        #       - parameter arguments that need to have a modified value / dimensions
        #       - all arguments that need to source from a general argument with a different name
        ####################################
        input:

          # File argument
          <file_argument_name>:
            argument_type: file.<format>     # bam, fastq, bwt ...
            # Linking fields
            #   These are optional fields
            #   Check https://magma-suite.readthedocs.io/en/latest/meta-workflow.html
            #     for more details
            source: <workflow_name>[@<tag>]
            source_argument_name: <file_argument_name>
            # Input dimension
            #   These are optional fields to specify input argument dimensions to use
            #     when creating the pipeline structure or step specific inputs
            #   See https://magma-suite.readthedocs.io/en/latest/meta-workflow.html
            #     for more details
            scatter: <integer>
            gather: <integer>
            input_dimension: <integer>
            extra_dimension: <integer>
            gather_input: <integer>
            # All the following fields are optional and provided as example,
            #   can be expanded to anything accepted by the schema
            mount: <boolean>
            rename: formula:<parameter_argument_name>
                  #  can be used to specify a name for parameter argument
                  #    to use to set a rename field for the file
            unzip: <string>

          # Parameter argument
          <parameter_argument_name>:
            argument_type: parameter.<type>
            # All the following fields are optional and provided as example,
            #   can be expanded to anything accepted by the schema
            value: <...>
            source_argument_name: <parameter_argument_name>

        ## Output ##########################
        #     Output files for the workflow
        ####################################
        output:

          # File output
          <file_output_name>:
            data_category:
              - <string>
            data_type:
              - <string>
            # All the following fields are optional and provided as example,
            #   can be expanded to anything accepted by the schema
            description: <string>
            variant_types:
              - <string>
            s3_lifecycle_category: <string>   # short_term_access_long_term_archive,
                                              # short_term_access, short_term_archive,
                                              # long_term_access_long_term_archive,
                                              # long_term_access, long_term_archive,
                                              # no_storage, ignore

        ## EC2 Configuration to use ########
        ####################################
        config:
          <config_parameter>: <...>


General Fields Definition
+++++++++++++++++++++++++

Required
^^^^^^^^
All the following fields are required.

name
----
Name of the pipeline, **MUST BE GLOBALLY UNIQUE (ACROSS THE PORTAL OBJECTS)**.

description
-----------
Description of the pipeline.

category
--------
Categories for the pipeline, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.

input
-----
Description of general input files and parameters for the pipeline. See :ref:`Input Definition <input>`.

workflows
---------
Description of workflows that are steps of the pipeline. See :ref:`Workflows Definition <workflows>`.

Optional
^^^^^^^^
All the following fields are optional and provided as example. Can be expanded to anything accepted by the schema, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.


.. _workflows:

Workflows Definition
++++++++++++++++++++
Each workflow is defined by its name and represents a step of the pipeline. Additional subfields need to be specified.

The workflow name must follow the format ``<workflow_name>[@<tag>]``.
``<workflow_name>`` needs to match a workflow that has been previously defined, see :ref:`Workflow <workflow>`.
If the same workflow is used for multiple steps in the pipeline, a tag can be added to the name of the workflow after '@' to make it unique (e.g., a QC step that run twice at different moments of the pipeline).
If a ``<tag>`` is used while defining a workflow, ``<workflow_name>@<tag>`` must be used to reference the correct step as dependency.

dependencies
^^^^^^^^^^^^
Workflows that must complete before kicking the current step.
List of workflows in the the format ``<workflow_name>[@<tag>]``.

shards
^^^^^^
Allows to force a fixed shards structure for the current step.
Override input structure, scatter and gather dimensions.
Shards structure as list, e.g., ``[['0'], ['1'], ['2']]``.

version
^^^^^^^
Version to use for the corresponding workflow instead of the default specified for the repository.
Allows to lock the workflow to specific version.

input
^^^^^
Description of general arguments that need to be referenced and specific arguments for the step. See :ref:`Input Definition <input>`.

output
^^^^^^
Description of expected output files for the workflow.

Each output is defined by its name. Additional subfields can be specified.
See `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.

Each output name needs to match an output name that has been previously defined in the corresponding workflow, see :ref:`Workflow <workflow>`.

config
^^^^^^
Description of configuration parameters to run the workflow.
Any parameters can be defined here and will be used to configure the run in AWS (e.g., EC2 type, EBS size, ...).


.. _input:

Input Definition
++++++++++++++++
Each argument is defined by its name. Additional subfields need to be specified depending on the argument type.
Each argument name needs to match an argument name that has been previously defined in the corresponding workflow, see :ref:`Workflow <workflow>`.

argument_type
^^^^^^^^^^^^^
Definition of the type of the argument.

For a **file** argument, the argument type is defined as ``file.<format>``, where ``<format>`` is the format used by the file.
``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

For a **parameter** argument, the argument type is defined as ``parameter.<type>``, where ``<type>`` is the type of the value expected for the argument [string, integer, float, array, boolean, object].

files
^^^^^
This field can be used to assign specific files to a **file** argument.
For example, specific reference files that are constant for the pipeline can be specified for the corresponding argument using this field.

Each file is specified using the name of the file and the version in the format ``<file_name>@<version>``.
For reference files, each file needs to match a file reference that has been previously defined, see :ref:`File Reference <file_reference>`.

value
^^^^^
This field can be used to assign a specific value to a **parameter** argument.

Example

.. code-block:: yaml

  a_float:
  argument_type: parameter.float
  value: 0.8

  an_integer:
  argument_type: parameter.integer
  value: 1

  a_string_array:
  argument_type: parameter.array
  value: ["DEL", "DUP"]

Linking Fields
^^^^^^^^^^^^^^
These are optional fields that can be used when defining workflow specific arguments to describe dependencies and map to arguments with different names.
See `magma documentation <https://magma-suite.readthedocs.io/en/latest/meta-workflow.html>`__ for for more details.

source
------
This field can be used to assign a dependency for a **file** argument to a previous workflow.
It must follow the format ``<workflow_name>[@<tag>]`` to reference the correct step as source.

source_argument_name
--------------------
This field can be used to source a specific argument by name.
It can be used to:

  - Specify the name of an output of a source step to use.
  - Specify the name of a general argument defined in the input section to use when it differs from the argument name.

Input Dimension Fields
^^^^^^^^^^^^^^^^^^^^^^
These are optional fields that can be used when defining workflow specific arguments to specify the input dimensions to use when creating the pipeline structure or step specific inputs.
See `magma documentation <https://magma-suite.readthedocs.io/en/latest/meta-workflow.html>`__ for more details.

scatter
-------
Input dimension to use to scatter the workflow.
This will create multiple shards in the pipeline for the step.
The same dimension will be used to subset the input when creating the specific input for each shard.

gather
------
Increment for input dimension when gathering from previous shards.
This will collate multiple shards into a single step.
The same increment in dimension will be used when creating the specific input for the step.

input_dimension
---------------
Additional dimension used to subset the input when creating the specific input for the step.
This will be applied on top of ``scatter``, if any, and will only affect the input.
This will not affect the scatter dimension used to create the shards for the step.

extra_dimension
---------------
Additional increment to dimension used when creating the specific input for the step.
This will be applied on top of ``gather``, if any, and will only affect the input.
This will not affect gather dimension in building the pipeline structure.

gather_input
------------
Equivalent to ``gather`` in collecting output from previous shards.
This will not affect scatter or gather dimensions in building pipeline structure.
