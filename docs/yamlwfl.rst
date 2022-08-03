
.. code-block:: python

    ## Workflow information #####################################
    #     General information for the workflow
    #############################################################
    name: <string> # name of the workflow
                   #   !!! must be unique !!!
    description: <string>

    runner: # Workflow description
      language: <language> # Language used in workflow description
                           #   <language> -> WDL, CWL
      main: <description> # Main description file
                          #   <description> -> .cwl, .wdl
      child: # Supplementary description files used by main
        - <description>

    # All the following tags are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    title: <string> # Title of the workflow

    software: # Software used by the workflow
      - <software>@<version|commit> # name for the software with version (either version or commit)
                                    #   Need to match a version for the software defined on the portal
                                    #   See software schema here
                                    #

    ## Input information ########################################
    #     Input files and parameters
    #############################################################
    input:

      a_file: # name of the argument
              #   !!! must be unique !!!
        argument_type: file.<format>
                       # <format> -> bam, fastq, bwt, ...
                       #   Need to match a format defined on the portal

      a_parameter:
        argument_type: parameter.<type>
                       # <type> -> string, integer, float, json, boolean

    ## Output information #######################################
    #     Output files and quality controls
    #############################################################
    output:

      a_file:
        argument_type: file.<format>
        secondary_files: # Secondary files to return for a_file
          - <format> # <format> -> bam, fastq, bwt, ...
                     #   Need to match a format defined on the portal

      a_qc:
        argument_type: qc.<type>
                       # <type> -> qc_type, e.g, quality_metric_vcfcheck
                       #   Need to match a qc_type on the portal defined in schemas
                       #   https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas
        argument_to_be_attached_to: <name> # name of the argument to attach the qc to
                                          #   e.g., <name> -> a_file
        # All the following tags are optional and provided as example,
        #   can be expanded to anything accepted by the schema
        zipped: <boolean>
        html: <boolean>
        json: <boolean>
        table: <boolean>
