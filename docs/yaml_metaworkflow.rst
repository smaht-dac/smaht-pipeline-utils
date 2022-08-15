
.. code-block:: python

    ## Pipeline information #####################################
    #     General information for the pipeline
    #############################################################
    name: <string> # name of the pipeline
                   #   !!! must be unique !!!
    description: <string>

    # All the following tags are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    title: <string> # Title of the pipeline

    ## General arguments ########################################
    #     Pipeline input, reference files, and general arguments
    #       define all arguments for the pipeline here
    #############################################################
    input:

      a_file: # name of the argument
              #   !!! must be unique !!!
        argument_type: file.<format>
                       # <format> -> bam, fastq, bwt, ...
                       #   Need to match a format defined on the portal
        # All the following tags are optional and provided as example,
        #   can be expanded to anything accepted by the schema
        # Check https://magma-suite.readthedocs.io/en/latest/meta-workflow.html
        #   for more details
        dimensionality: <integer>
        files: # This tag allows to specify reference files that are constant for the pipeline
          - <name>@<version> # name and version of the reference file
                             #   Need to match a reference file defined on the portal

      a_parameter:
        argument_type: parameter.<type>
                       # <type> -> string, integer, float, json, boolean
        # All the following tags are optional and provided as example,
        #   can be expanded to anything accepted by the schema
        value: <...>

    ## Workflows and dependencies ###############################
    #     Information for the workflows and their dependencies
    #############################################################
    workflows:

      ## Workflow definition #####################
      ############################################
      a_workflow: # name of the workflow
                  #   !!! must be unique !!!
                  #   Need to match a workflow defined on the portal

        ## Specific arguments ##############
        #   General arguments that require some tweaking and
        #     specific arguments for the workflow:
        #       - file arguments that need to source the output from a previous step
        #       - file arguments that need to scatter or gather
        #       - parameter arguments that need to have a modified value / dimensions
        #       - all arguments that need to source from a general argument with a different name
        ####################################
        input:

          a_file: # name of the argument
                  #   !!! must be unique !!!
            argument_type: file.<format>
                           # <format> -> bam, fastq, bwt, ...
                           #   Need to match a format defined on the portal
            # Linking fields
            #   These are optional fields
            #   Check https://magma-suite.readthedocs.io/en/latest/meta-workflow.html
            #     for more details
            source: <string> # name of the source step to get the argument from
            source_argument_name: <string> # name of the argument to get
                                           #  - name of an output of source step
                                           #  - name of general argument to use
            # Input dimension
            #   These are optional fields to specify input argument dimensions to use
            #     when creating the pipeline structure or step specific inputs
            #   See https://magma-suite.readthedocs.io/en/latest/meta-workflow.html
            #     for more details
            scatter: <integer> # Input argument dimension to use to scatter the step
            gather: <integer> # Increment for input argument dimension when gathering from previous steps
            input_dimension: <integer> # Additional dimension used to subset the input argument when creating the step specific input
            extra_dimension: <integer> # Additional increment to dimension used when creating the step specific input
            # All the following tags are optional and provided as example,
            #   can be expanded to anything accepted by the schema
            mount: <boolean>
            rename: formula:<parameter_name>
                  #  !!! formula:<parameter_name> can be used to specify a name
                  #    for parameter argument to use to set a rename tag for the file !!!
            unzip: <string>

          a_parameter:
            argument_type: parameter.<type>
                           # <type> -> string, integer, float, json, boolean
            # All the following tags are optional and provided as example,
            #   can be expanded to anything accepted by the schema
            value: <...>
            source_argument_name: <string> # name of general argument to use

        ## Output ##########################
        #     Output files for the workflow
        ####################################
        output:

          a_file: # name of the output
                  #   !!! must be unique !!!
            # All the following tags are optional and provided as example,
            #   can be expanded to anything accepted by the schema
            # Check https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas
            #   for more information
            description: <string>
            file_type: <file_type>
                       # <file_type> -> ...
            linkto_location:
              - <location>
                # <location> -> Sample, SampleProcessing, ...
            higlass_file: <boolean>
            variant_type: <variant_type>
                          # <variant_type> -> SNV, SV, CNV

        ## EC2 Configuration to use ########
        ####################################
        config:
          a_config: <...>
          another_config: <...>
