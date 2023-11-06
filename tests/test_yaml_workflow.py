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
                "name": "gatk-HaplotypeCaller",
                "version": "v1.0.0",
                "category": ["Annotation"],
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
                      "argument_type": "Generic QC file",
                      "qc_json": True,
                      "qc_zipped": False,
                      "workflow_argument_name": "vcfcheck",
                      "argument_format": "json"
                    }
                ],
                "description": "Run HaplotypeCaller from gatk package",
                "submission_centers": ["hms-dbmi"],
                "consortia": ["cgap-core"],
                "software": [
                    "cgap-core:Software-gatk_4.2.1",
                    "cgap-core:Software-vcf-tools_5A63Aa1"
                ],
                "title": "HaplotypeCaller plus integity-check [v1.0.0]",
                "child_file_names": [
                    "gatk-HaplotypeCaller.wdl",
                    "integrity-check.wdl"
                ],
                "directory_url": "s3://BUCKETCWL/test_pipeline/v1.0.0",
                "main_file_name": "workflow_gatk-HaplotypeCaller-check.wdl",
                "language": "WDL"
            },
            {
                "accession": "GAPFIXRDPDK1",
                "category": ["Feature Calling"],
                "aliases": ["cgap-core:Workflow-gatk-HaplotypeCaller_v1.0.0"],
                "name": "gatk-HaplotypeCaller",
                "version": "v1.0.0",
                "arguments": [
                    {
                      "argument_format": "bam",
                      "argument_type": "Input file",
                      "workflow_argument_name": "input_bam"
                    },
                    {
                      "argument_format": "vcf",
                      "argument_type": "Output processed file",
                      "workflow_argument_name": "output_vcf"
                    }
                ],
                "description": "Run HaplotypeCaller from gatk package",
                "submission_centers": ["hms-dbmi"],
                "consortia": ["cgap-core"],
                "title": "gatk-HaplotypeCaller [v1.0.0]",
                "directory_url": "s3://BUCKETCWL/test_pipeline/v1.0.0",
                "main_file_name": "gatk-HaplotypeCaller-check.cwl",
                "uuid": "1936f246-22e1-45dc-bb5c-9cfd55537fe9",
                "language": "CWL"
            }
        ]

    for d in yaml_parser.load_yaml('tests/repo_correct/portal_objects/workflows/A_gatk-HC.yaml'):
        d_ = yaml_parser.YAMLWorkflow(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-core"],
                            version='v1.0.0',
                            wflbucket_url='s3://BUCKETCWL/test_pipeline/v1.0.0'
                        )
        # check
        assert d_ == res[0]

    for d in yaml_parser.load_yaml('tests/repo_correct/portal_objects/workflows/B_minimal-gatk-HC.yaml'):
        d_ = yaml_parser.YAMLWorkflow(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-core"],
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
                                    submission_centers=["hms-dbmi"],
                                    consortia=["cgap-core"],
                                    version='v1.0.0',
                                    wflbucket_url='s3://BUCKETCWL/test_pipeline/v1.0.0'
                                )
            except yaml_parser.ValidationError as e:
                pass
