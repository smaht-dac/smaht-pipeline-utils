=========
Functions
=========

Collection of utilities available as functions:

  - :ref:`check_lines <check_lines>`

.. _check_lines:

check_lines
+++++++++++

*check_lines* function can be used to check that line counts are matching between the output of two steps where lines should not be dropped (i.e., any steps that modify without filtering), or between an output bam and the input fastq files.
Requires uuid for the MetaWorkflowRun object to check and ff_key to access the metadata on the portal. The steps to compare are specified as dictionaries, examples below.

.. code-block:: python

    from pipeline_utils.lib import check_lines

    result <bool> = check_lines.check_lines(metawfr_uuid, ff_key, steps=steps_dict, fastqs=fastqs_dict)

    # metawfr_uuid
    #   -> uuid for MetaWorkflowRun object

    # ff_key
    #   -> key to authenticate on the portal

    ## steps_dict example
    # steps_dict = {
    #     'workflow_add-readgroups-check': {
    #                         'dependency': 'workflow_bwa-mem_no_unzip-check',
    #                         'output': 'bam_w_readgroups',
    #                         'output_match': 'raw_bam',
    #                         'key': 'Total Reads',
    #                         'key_match': 'Total Reads'
    #                         },
    #     ...
    # }

    ## fastqs_dict example
    # fastqs_dict = {
    #     'workflow_bwa-mem_no_unzip-check': {
    #                          'output': 'raw_bam',
    #                          'input_match': ['fastq_R1', 'fastq_R2'],
    #                          'key': 'Total Reads',
    #                          'key_match': 'Total Sequences'
    #                          },
    #     ...
    # }
