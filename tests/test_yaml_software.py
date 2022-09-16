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
                "aliases": ["cgap-core:gatk_4.1.2"],
                "description": "gatk software package",
                "institution": "/institutions/hms-dbmi/",
                "name": "gatk",
                "project": "/projects/cgap-core/",
                "source_url": "http:/broad",
                "title": "gatk 4.1.2",
                "version": "4.1.2"
            },
            {
                "accession": "GAPMKF1LL29K",
                "aliases": ["cgap-core:picard_324ePT"],
                "commit": "324ePT",
                "institution": "/institutions/hms-dbmi/",
                "name": "picard",
                "project": "/projects/cgap-core/",
                "title": "picard, 324ePT",
                "uuid": "efdac7ec-7da3-4f23-9056-7a04abbc5e8b"
            }
        ]

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_correct/portal_objects/software.yaml')):
        # creating JSON object
        d_ = yaml_parser.YAMLSoftware(d).to_json(
                            institution='hms-dbmi',
                            project='cgap-core'
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
                                institution='hms-dbmi',
                                project='cgap-core'
                                )
        except yaml_parser.ValidationError as e:
            pass
