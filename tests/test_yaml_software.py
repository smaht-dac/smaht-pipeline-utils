#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
from pipeline_utils.lib import yaml_parser

#################################################################
#   Tests
#################################################################
def test_software():
    """
    """
    res = [
            {
                "aliases": ["cgap-core:Software-gatk_4.1.2"],
                "description": "gatk software package",
                "submission_centers": ["hms-dbmi"],
                "name": "gatk",
                "consortia": ["cgap-core"],
                "source_url": "http:/broad",
                "title": "gatk 4.1.2",
                "version": "4.1.2",
                "category": "Aligner"
            },
            {
                "accession": "GAPMKF1LL29K",
                "aliases": ["cgap-core:Software-picard_324ePT"],
                "commit": "324ePT",
                "submission_centers": ["hms-dbmi"],
                "name": "picard",
                "consortia": ["cgap-core"],
                "title": "picard [324ePT]",
                "uuid": "efdac7ec-7da3-4f23-9056-7a04abbc5e8b",
                "category": "Variant Caller"
            }
        ]

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_correct/portal_objects/software.yaml')):
        # creating JSON object
        d_ = yaml_parser.YAMLSoftware(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-core"]
                            )
        # check
        assert d_ == res[i]

def test_software_error():
    """
    """

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_error/portal_objects/software.yaml')):
        try:
            # creating JSON object
            d_ = yaml_parser.YAMLSoftware(d).to_json(
                                submission_centers=["hms-dbmi"],
                                consortia=["cgap-core"]
                                )
        except yaml_parser.ValidationError as e:
            pass
