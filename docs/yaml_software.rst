.. _software:

========
Software
========

This documentation provides a comprehensive guide to the template structure necessary for implementing *Software* objects.
These objects enable users to codify information to track and version specific softwares used by the pipeline.

Template
++++++++

.. code-block:: python

    ## Software information #####################################
    #     Information for software
    #############################################################
    # All the following fields are required
    name: <string>

    # Either version or commit is required to identify the software
    version: <string>
    commit: <string>

    category:
      - <string>                      # Quality Control

    # All the following fields are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas
    source_url: <string>
    description: <string>
    license: <string>                 # MIT, GPLv3, ...


Fields Definition
+++++++++++++++++

Required
^^^^^^^^
All the following fields are required.
Either *version* or *commit* is required to identify the software.

name
----
Name of the software, **MUST BE GLOBALLY UNIQUE (ACROSS THE PORTAL OBJECTS)**.

version
-------
Version of the software.

commit
------
Commit of the software.

category
--------
Categories for the software, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.

Optional
^^^^^^^^
All the following fields are optional and provided as example. Can be expanded to anything accepted by the schema, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.

source_url
----------
URL for the software (e.g, source files, binaries, repository, etc...).

description
-----------
Description for the software.

license
-------
License information.
