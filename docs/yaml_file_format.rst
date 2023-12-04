.. _file_format:

===========
File Format
===========

This documentation provides a comprehensive guide to the template structure necessary for implementing *File Format* objects.
These objects enable users to codify file formats used by the pipeline.

Template
++++++++

.. code-block:: python

    ## File Format information ##################################
    #     Information for file format
    #############################################################
    # All the following fields are required
    name: <string>
    extension: <extension>    # fa, fa.fai, dict, ...
    description: <string>

    # All the following fields are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas
    secondary_formats:
      - <format>              # bam, fastq, bwt, ...


Fields Definition
+++++++++++++++++

Required
^^^^^^^^
All the following fields are required.

name
----
Name of the file format, **MUST BE GLOBALLY UNIQUE (ACROSS THE PORTAL OBJECTS)**.

extension
---------
Extension used by the file format.

description
-----------
Description of the file format.

Optional
^^^^^^^^
All the following fields are optional and provided as example. Can be expanded to anything accepted by the schema, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.

secondary_formats
-----------------
List of secondary ``<format>`` available for the file format.
Each ``<format>`` needs to match a file format that has been previously defined.
