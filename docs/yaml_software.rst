
.. code-block:: python

    ## Software information #####################################
    #     Information for software
    #############################################################
    name: <string> # name of the software
                   #   !!! must be unique !!!

    # One between version or commit is required to version the software
    version: <string> # Version of the software
    commit: <string>  # Commit of the software

    # All the following tags are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas
    title: <string> # Title for the software
    source_url: <string>  # URL for the software
                          #   -> source files, binaries, repository
    description: <string> # Description for the software
