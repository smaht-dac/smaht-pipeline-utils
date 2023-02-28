#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
import glob
from pipeline_utils.lib import yaml_parser

#################################################################
#   Tests
#################################################################
def test_workflow():
    """
    """
    res = [
            {
                "aliases": ["cgap-core:Workflow-gatk-HaplotypeCaller_v1.0.0"],
                "app_name": "gatk-HaplotypeCaller",
                "app_version": "v1.0.0",
                "arguments": [
                    {
                      "argument_format": "bam",
                      "argument_type": "Input file",
                      "workflow_argument_name": "input_bam"
                    },
                    {
                      "argument_type": "parameter",
                      "workflow_argument_name": "nthreads"
                    },
                    {
                      "argument_format": "vcf_gz",
                      "argument_type": "Output processed file",
                      "secondary_file_formats": [
                        "vcf_gz_tbi"
                      ],
                      "workflow_argument_name": "output_vcf"
                    },
                    {
                      "argument_to_be_attached_to": "output_vcf",
                      "argument_type": "Output QC file",
                      "qc_html": False,
                      "qc_json": True,
                      "qc_table": False,
                      "qc_type": "quality_metric_vcfcheck",
                      "qc_zipped": False,
                      "workflow_argument_name": "vcfcheck"
                    }
                ],
                "description": "Run HaplotypeCaller from gatk package",
                "institution": "/institutions/hms-dbmi/",
                "name": "gatk-HaplotypeCaller_v1.0.0",
                "project": "/projects/cgap-core/",
                "software": [
                    "cgap-core:Software-gatk_4.2.1",
                    "cgap-core:Software-vcf-tools_5A63Aa1"
                ],
                "title": "HaplotypeCaller plus integity-check [v1.0.0]",
                "wdl_child_filenames": [
                    "gatk-HaplotypeCaller.wdl",
                    "integrity-check.wdl"
                ],
                "wdl_directory_url": "s3://BUCKETCWL/test_pipeline/v1.0.0",
                "wdl_main_filename": "workflow_gatk-HaplotypeCaller-check.wdl",
                "workflow_language": "wdl"
            },
            {
                "accession": "GAPFIXRDPDK1",
                "aliases": ["cgap-core:Workflow-gatk-HaplotypeCaller_v1.0.0"],
                "app_name": "gatk-HaplotypeCaller",
                "app_version": "v1.0.0",
                "arguments": [
                    {
                      "argument_format": "bam",
                      "argument_type": "Input file",
                      "workflow_argument_name": "input_bam"
                    },
                    {
                      "argument_format": "vcf",
                      "argument_type": "Output processed file",
                      "secondary_file_formats": [],
                      "workflow_argument_name": "output_vcf"
                    }
                ],
                "description": "Run HaplotypeCaller from gatk package",
                "institution": "/institutions/hms-dbmi/",
                "name": "gatk-HaplotypeCaller_v1.0.0",
                "project": "/projects/cgap-core/",
                "software": [],
                "title": "gatk-HaplotypeCaller [v1.0.0]",
                "cwl_child_filenames": [],
                "cwl_directory_url_v1": "s3://BUCKETCWL/test_pipeline/v1.0.0",
                "cwl_main_filename": "gatk-HaplotypeCaller-check.cwl",
                "uuid": "1936f246-22e1-45dc-bb5c-9cfd55537fe9"
            }
        ]

    for d in yaml_parser.load_yaml('tests/repo_correct/portal_objects/workflows/A_gatk-HC.yaml'):
        d_ = yaml_parser.YAMLWorkflow(d).to_json(
                            institution='hms-dbmi',
                            project='cgap-core',
                            version='v1.0.0',
                            wflbucket_url='s3://BUCKETCWL/test_pipeline/v1.0.0'
                        )
        # check
        assert d_ == res[0]

    for d in yaml_parser.load_yaml('tests/repo_correct/portal_objects/workflows/B_minimal-gatk-HC.yaml'):
        d_ = yaml_parser.YAMLWorkflow(d).to_json(
                            institution='hms-dbmi',
                            project='cgap-core',
                            version='v1.0.0',
                            wflbucket_url='s3://BUCKETCWL/test_pipeline/v1.0.0'
                        )
        # check
        assert d_ == res[1]


def test_workflow_error():
    """
    """

    for i, fn in enumerate(glob.glob('tests/repo_error/portal_objects/workflows/*.yaml')):
        for d in yaml_parser.load_yaml(fn):
            try:
                d_ = yaml_parser.YAMLWorkflow(d).to_json(
                                    institution='hms-dbmi',
                                    project='cgap-core',
                                    version='v1.0.0',
                                    wflbucket_url='s3://BUCKETCWL/test_pipeline/v1.0.0'
                                )
            except yaml_parser.ValidationError as e:
                pass
