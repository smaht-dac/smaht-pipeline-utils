
.. code-block:: python

    ## File Format information ##################################
    #     Information for file format
    #############################################################
    name: <string> # name of the file format
                   #   !!! must be unique !!!
    extension: <extension>  # Extension used for the file format
                            #   <extension> -> fa, fa.fai, dict, ...
    description: <string> # Description of the file format

    # All the following tags are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas
    secondary_formats: # Secondary formats available for the file format
      - <format> # <format> -> bam, fastq, bwt, ...
                 #   Need to match a format defined on the portal
    file_types: # File types that can use the format
      - <filetype> # <filetype> -> FileReference, FileProcessed
                   #   default is [FileReference, FileProcessed]
    status: <status> # <status> -> shared, ...
                     #   default is shared
