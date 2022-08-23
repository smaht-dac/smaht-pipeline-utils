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
                "aliases": ["bam"],
                "description": "format to represent aligned reads",
                "extrafile_formats": ["bai"],
                "file_format": "bam",
                "institution": "/institutions/hms-dbmi/",
                "project": "/projects/cgap-core/",
                "standard_file_extension": "bam",
                "status": "shared",
                "valid_item_types": ["FileReference", "FileProcessed"]
            },
            {
                "accession": 'GAPFIXRDPDK1',
                "aliases": ["bam_bai"],
                "description": "index for bam format",
                "extrafile_formats": [],
                "file_format": "bam_bai",
                "institution": "/institutions/hms-dbmi/",
                "project": "/projects/cgap-core/",
                "standard_file_extension": "bam.bai",
                "status": "shared",
                "valid_item_types": ["FileReference", "FileProcessed"],
                "uuid": '1936f246-22e1-45dc-bb5c-9cfd55537fe9'
            }
        ]

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_correct/portal_objects/file_format.yaml')):
        # creating JSON object
        d_ = yaml_parser.YAMLFileFormat(d).to_json(
                            INSTITUTION='hms-dbmi',
                            PROJECT='cgap-core'
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
                                INSTITUTION='hms-dbmi',
                                PROJECT='cgap-core'
                                )
        except yaml_parser.SchemaError as e:
            assert e.args[0] == 'YAML object failed schema validation'
