#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
from pipeline_utils.lib import yaml_parser

#################################################################
#   Tests
#################################################################
def test_file_format():
    """
    """
    res = [
            {
                "aliases": ["cgap-core:FileFormat-bam"],
                "description": "format to represent aligned reads",
                "extra_file_formats": ["bai"],
                "identifier": "bam",
                "submission_centers": ["hms-dbmi"],
                "consortia": ["cgap-core"],
                "standard_file_extension": "bam",
                "status": "shared"
                # "valid_item_types": ["FileReference", "FileProcessed"]
            },
            {
                "accession": 'GAPFIXRDPDK1',
                "aliases": ["cgap-core:FileFormat-bam_bai"],
                "description": "index for bam format",
                "identifier": "bam_bai",
                "submission_centers": ["hms-dbmi"],
                "consortia": ["cgap-core"],
                "standard_file_extension": "bam.bai",
                "status": "shared",
                # "valid_item_types": ["FileReference", "FileProcessed"],
                "uuid": '1936f246-22e1-45dc-bb5c-9cfd55537fe9'
            }
        ]

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_correct/portal_objects/file_format.yaml')):
        # creating JSON object
        d_ = yaml_parser.YAMLFileFormat(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-core"]
                            )
        # check
        assert d_ == res[i]

def test_file_format_error():
    """
    """

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_error/portal_objects/file_format.yaml')):
        try:
            # creating JSON object
            d_ = yaml_parser.YAMLFileFormat(d).to_json(
                                submission_centers=["hms-dbmi"],
                                consortia=["cgap-core"]
                                )
        except yaml_parser.ValidationError as e:
            pass
