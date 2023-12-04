.. _file_reference:

==============
File Reference
==============

This documentation provides a comprehensive guide to the template structure necessary for implementing *File Reference* objects.
These objects enable users to codify information to track and version the reference files used by the pipeline.

Template
++++++++

.. code-block:: python

    ## File Reference information ###############################
    #     Information for reference file
    #############################################################
    # All the following fields are required
    name: <string>
    description: <string>
    format: <format>              # bam, fastq, bwt, ...
    version: <string>

    category:
      - <category>                # Reference Genome, ...
    type:
      -  <type>                   # Reference Sequence, ...

    # All the following fields are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas
    secondary_files:
      - <format>                  # bam, fastq, bwt, ...
    status: <status>              # uploading, uploaded
    license: <string>             # MIT, GPLv3, ...

    # Required to enable sync with a reference bucket
    uuid: <uuid4>
    accession: <accession>


Fields Definition
+++++++++++++++++

Required
^^^^^^^^
All the following fields are required.

name
----
Name of the reference file, **MUST BE GLOBALLY UNIQUE (ACROSS THE PORTAL OBJECTS)**.

description
-----------
Description of the reference file.

format
------
File format used by the reference file.
``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

version
-------
Version of the reference file.

Optional
^^^^^^^^
All the following fields are optional and provided as example. Can be expanded to anything accepted by the schema, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.

secondary_files
---------------
List of ``<format>`` for secondary files associated to the reference file.
Each ``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

status
------
Status of the upload.
The possible values are ``uploading`` and ``uploaded``.
If no value is specified, the status will not be updated during patching and set to ``uploading`` if posting the object for the first time.

Most likely you don't want to set this field and just use the default logic automatically applied during deployment.

license
-------
License information.

category
--------
Categories for the reference file, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.

type
----
Types for the reference file, see `schemas <https://github.com/smaht-dac/smaht-portal/tree/main/src/encoded/schemas>`__.
