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
                "submission_centers": ["hms-dbmi"],
                "consortia": ["cgap-core"],
                "status": "uploading",
                "uuid": "1936f246-22e1-45dc-bb5c-9cfd55537fe7",
                "data_category": ["Sequencing Reads"],
                "data_type": ["Unaligned Reads"]
            },
            {
                "aliases": ["cgap-core:FileReference-reference_genome_hg38"],
                "description": "hg38 full reference genome plus decoy for CGAP, fasta format",
                "file_format": "fa",
                "submission_centers": ["hms-dbmi"],
                "consortia": ["cgap-core"],
                "status": None,
                "data_category": ["Sequencing Reads"],
                "data_type": ["Aligned Reads"]
            }
        ]

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_correct/portal_objects/file_reference.yaml')):
        # creating JSON object
        d_ = yaml_parser.YAMLFileReference(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-core"]
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
                                submission_centers=["hms-dbmi"],
                                consortia=["cgap-core"]
                                )
        except yaml_parser.ValidationError as e:
            pass
