
.. code-block:: python

    ## File Reference information ###############################
    #     Information for reference file
    #############################################################
    name: <string> # name of the reference file
                   #   !!! must be unique !!!
    description: <string> # Description of the reference file
    format: <format> # <format> -> bam, fastq, bwt, ...
                     #   Need to match a format defined on the portal
    version: <string> # Version of the reference file

    # All the following tags are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas
    secondary_files: # Secondary files for the reference file
      - <format> # <format> -> bam, fastq, bwt, ...
                 #   Need to match a format defined on the portal
    status: <status> # Status of the upload
                     #  <status> -> uploading, uploaded
                     #  default is None -> the status will not be updated during patch,
                     #    and set to uploading if post for the first time
