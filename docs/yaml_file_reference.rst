.. _file_reference:

==============
File Reference
==============

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

    # All the following fields are optional and provided as example,
    #   can be expanded to anything accepted by the schema
    #   https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas
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
Name of the reference file, **MUST BE GLOBALLY UNIQUE**.

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
All the following fields are optional and provided as example. Can be expanded to anything accepted by the schema, see `schemas <https://github.com/dbmi-bgm/cgap-portal/tree/master/src/encoded/schemas>`__.

secondary_files
---------------
List of ``<format>`` for secondary files associated to the reference file.
Each ``<format>`` needs to match a file format that has been previously defined, see :ref:`File Format <file_format>`.

status
------
Status of the upload.
The possible values are ``uploading`` and ``uploaded``.
If no value is specified, the status will not be updated during patching and set to ``uploading`` if posting for the first time.

license
-------
License information.
