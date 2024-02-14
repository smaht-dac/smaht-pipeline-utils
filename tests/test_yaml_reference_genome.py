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
        {"code": "GRCh38",
         "title": "GRCh38 [GCA_000001405.15]",
         "consortia": ["cgap-core"],
         "identifier": "grch38",
         "submission_centers": ["hms-dbmi"],
         "uuid": "e89937e6-80d3-4605-8dea-4a74c7981a9f",
         "files": [
            "cgap-core:ReferenceFile-complete-reference-fasta-no-alt_GCA_000001405.15_GRCh38_no_decoy",
            "cgap-core:ReferenceFile-complete-reference-bwt-no-alt_GCA_000001405.15_GRCh38_no_decoy"
         ],
         "aliases": ["cgap-core:ReferenceGenome-GRCh38_GCA_000001405.15"]}

        ]

    for i, d in enumerate(yaml_parser.load_yaml('tests/repo_correct/portal_objects/reference_genome.yaml')):
        # creating JSON object
        d_ = yaml_parser.YAMLReferenceGenome(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-core"]
                            )
        # check
        assert d_ == res[i]
