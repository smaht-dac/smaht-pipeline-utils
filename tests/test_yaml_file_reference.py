#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
from pipeline_utils.lib import yaml_parser

#################################################################
#   Tests
#################################################################
def test_file_reference():
    """
    """
    res = [
            {
                "accession": "GAPFIXRDPDK5",
                "aliases": ["cgap-core:FileReference-reference_genome_hg38"],
                "description": "hg38 full reference genome plus decoy for CGAP, fasta format",
                "extra_files": ["fa_fai", "dict"],
                "file_format": "fa",
                "institution": "/institutions/hms-dbmi/",
                "project": "/projects/cgap-core/",
                "status": "uploading",
                "uuid": "1936f246-22e1-45dc-bb5c-9cfd55537fe7"
            },
            {
                "aliases": ["cgap-core:FileReference-reference_genome_hg38"],
                "description": "hg38 full reference genome plus decoy for CGAP, fasta format",
                "extra_files": [],
                "file_format": "fa",
                "institution": "/institutions/hms-dbmi/",
                "project": "/projects/cgap-core/",
                "status": None
            }
        ]

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_correct/portal_objects/file_reference.yaml')):
        # creating JSON object
        d_ = yaml_parser.YAMLFileReference(d).to_json(
                            institution='hms-dbmi',
                            project='cgap-core'
                            )
        # check
        assert d_ == res[i]

def test_file_reference_error():
    """
    """

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_error/portal_objects/file_reference.yaml')):
        try:
            # creating JSON object
            d_ = yaml_parser.YAMLFileReference(d).to_json(
                                institution='hms-dbmi',
                                project='cgap-core'
                                )
        except yaml_parser.ValidationError as e:
            pass
