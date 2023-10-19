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
def test_metaworkflow():
    """
    """
    res = [
        {
          "aliases": ["cgap-core:MetaWorkflow-gatk-HC-GT-pipeline_v1.0.0"],
          "description": "Pipeline to run gatk-HC and gatk-GT to call and genotype variants",
          "category": ["Alignment", "Format Conversion"],
          "input": [
            {
              "argument_name": "input_vcf",
              "argument_type": "file",
              "dimensionality": 1
            },
            {
              "argument_name": "reference",
              "argument_type": "file",
              "files": [{"file": "cgap-core:FileReference-reference_genome_hg38"}]
            },
            {
              "argument_name": "samples",
              "argument_type": "parameter",
              "value": ["SAMPLENAME"],
              "value_type": "json"
            }
          ],
          "submission_centers": ["hms-dbmi", "smaht-dbmi"],
          "name": "gatk-HC-GT-pipeline",
          "consortia": ["cgap-core"],
          "title": "gatk-HC and gatk-GT pipeline [v1.0.0]",
          "version": "v1.0.0",
          "workflows": [
            {
              "config": {
                "ebs_size": "2x",
                "ec2_type": "m.5xlarge"
              },
              "custom_pf_fields": {
                "HC_vcf": {
                  "description": "output from gatk-HC",
                  "file_type": "hc-vcf",
                  "linkto_location": [
                    "SampleProcessing"
                  ]
                }
              },
              "input": [
                {
                  "argument_name": "vcf",
                  "argument_type": "file",
                  "extra_dimension": 1,
                  "mount": True,
                  "source_argument_name": "input_vcf",
                  "unzip": "gz"
                },
                {
                  "argument_name": "reference_genome",
                  "argument_type": "file",
                  "source_argument_name": "reference"
                },
                {
                  "argument_name": "nthreads",
                  "argument_type": "parameter",
                  "value": 16,
                  "value_type": "integer"
                }
              ],
              "name": "gatk-HC",
              "workflow": "cgap-core:Workflow-gatk-HC_v1.0.0"
            },
            {
              "config": {
                "ebs_size": "3x",
                "ec2_type": "c.5xlarge"
              },
              "custom_pf_fields": {
                "GT_vcf": {
                  "description": "output from gatk-GT",
                  "file_type": "GT-vcf",
                  "higlass_file": True,
                  "variant_type": "SNV"
                }
              },
              "input": [
                {
                  "argument_name": "input_vcf_HC",
                  "argument_type": "file",
                  "gather": 0,
                  "scatter": 0,
                  "source": "gatk-HC",
                  "source_argument_name": "HC_vcf"
                },
                {
                  "argument_name": "sample_name",
                  "argument_type": "parameter",
                  "input_dimension": 1,
                  "source_argument_name": "samples",
                  "value_type": "json"
                }
              ],
              "name": "gatk-GT",
              "workflow": "cgap-core:Workflow-gatk-GT_v1.0.0"
            }
          ]
        },
        {
          "accession": "GAPFIXRDPDK1",
          "category": ["Variant Calling"],
          "aliases": ["cgap-core_cgap-test:MetaWorkflow-gatk-HC-pipeline_v1.0.0"],
          "description": "Pipeline to run gatk-HC to call variants",
          "input": [
            {
              "argument_name": "input_vcf",
              "argument_type": "file"
            },
            {
              "argument_name": "reference",
              "argument_type": "file",
              "files": [{"dimension": "0", "file": "cgap-core_cgap-test:FileReference-reference_genome_hg38"},
                        {"dimension": "1", "file": "cgap-core_cgap-test:FileReference-reference_bam_hg38"}]
            },
            {
              "argument_name": "samples",
              "argument_type": "parameter",
              "value_type": "json"
            }
          ],
          "submission_centers": ["hms-dbmi"],
          "name": "gatk-HC-pipeline",
          "consortia": ["cgap-test", "cgap-core"],
          "title": "gatk-HC-pipeline [v1.0.0]",
          "uuid": "1936f246-22e1-45dc-bb5c-9cfd55537fe9",
          "version": "v1.0.0",
          "workflows": [
            {
              "config": {
                "ebs_size": "2x",
                "ec2_type": "m.5xlarge"
              },
              "custom_pf_fields": {
                "HC_vcf": {
                  "file_type": "hc-vcf"
                }
              },
              "input": [
                {
                  "argument_name": "vcf",
                  "argument_type": "file",
                  "source_argument_name": "input_vcf"
                },
                {
                  "argument_name": "reference",
                  "argument_type": "file"
                },
                {
                  "argument_name": "samples",
                  "argument_type": "parameter",
                  "value_type": "json"
                }
              ],
              "name": "gatk-HC",
              "workflow": "cgap-core_cgap-test:Workflow-gatk-HC_v1.0.0"
            }
          ]
        }
    ]

    for d in yaml_parser.load_yaml('tests/repo_correct/portal_objects/metaworkflows/A_gatk-HC-GT.yaml'):
        d_ = yaml_parser.YAMLMetaWorkflow(d).to_json(
                            submission_centers=["hms-dbmi", "smaht-dbmi"],
                            consortia=["cgap-core"],
                            version='v1.0.0'
                        )
        # check
        assert d_ == res[0]

    for d in yaml_parser.load_yaml('tests/repo_correct/portal_objects/metaworkflows/B_minimal-gatk-HC-GT.yaml'):
        d_ = yaml_parser.YAMLMetaWorkflow(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-test", "cgap-core"],
                            version='v1.0.0'
                        )
        # check
        assert d_ == res[1]

def test_qc_ruleset():
    """
    """
    res = {
      "accession": "GAPFIXRDPDK1",
      "category": ["Variant Calling"],
      "aliases": ["cgap-core_cgap-test:MetaWorkflow-gatk-HC-pipeline_v1.0.0"],
      "description": "Pipeline to run gatk-HC to call variants",
      "input": [
        {
          "argument_name": "input_vcf",
          "argument_type": "file"
        },
        {
          "argument_name": "reference",
          "argument_type": "file",
          "files": [{"dimension": "0", "file": "cgap-core_cgap-test:FileReference-reference_genome_hg38"},
                    {"dimension": "1", "file": "cgap-core_cgap-test:FileReference-reference_bam_hg38"}]
        },
        {
          "argument_name": "samples",
          "argument_type": "parameter",
          "value_type": "json"
        },
        {
          "argument_name": "qc_ruleset_name_1",
          "argument_type": "parameter",
          "value_type": "qc_ruleset",
          "value": {
                  "qc_thresholds": [
                      {
                          "id": "c1",
                          "metric": "coverage",
                          "operator": ">=",
                          "pass_target": 100.0,
                          "warn_target": 80.0,
                          "use_as_qc_flag": True
                      },
                      {
                          "id": "c2",
                          "metric": "coverage",
                          "operator": "<=",
                          "pass_target": 200.0,
                          "warn_target": 180.0,
                      },
                      {
                          "id": "c3",
                          "metric": "coverage",
                          "operator": ">",
                          "pass_target": 80.0,
                          "warn_target": 3.3
                      },
                      {
                          "id": "rl",
                          "metric": "read_length",
                          "operator": "==",
                          "pass_target": "PASS",
                          "warn_target": "NOT PASS",
                          "use_as_qc_flag": True
                      }
                  ],
                  "overall_quality_status_rule": "( {c1} and {c2} ) or not ( {c3} and {rl} )"
              }
        }
      ],
      "submission_centers": ["hms-dbmi"],
      "name": "gatk-HC-pipeline",
      "consortia": ["cgap-test", "cgap-core"],
      "title": "gatk-HC-pipeline [v1.0.0]",
      "uuid": "1936f246-22e1-45dc-bb5c-9cfd55537fe9",
      "version": "v1.0.0",
      "workflows": [
        {
          "config": {
            "ebs_size": "2x",
            "ec2_type": "m.5xlarge"
          },
          "custom_pf_fields": {
            "HC_vcf": {
              "file_type": "hc-vcf"
            }
          },
          "input": [
            {
              "argument_name": "vcf",
              "argument_type": "file",
              "source_argument_name": "input_vcf"
            },
            {
              "argument_name": "reference",
              "argument_type": "file"
            },
            {
              "argument_name": "samples",
              "argument_type": "parameter",
              "value_type": "json"
            },
            {
              'argument_name': 'qc_ruleset',
              'argument_type': 'parameter',
              'value_type': 'qc_ruleset',
              'source_argument_name': 'qc_ruleset_name_1'
            }
          ],
          "name": "gatk-HC",
          "workflow": "cgap-core_cgap-test:Workflow-gatk-HC_v1.0.0"
        }
      ]
    }

    for d in yaml_parser.load_yaml('tests/repo_correct/portal_objects/metaworkflows/QC_test.yaml'):
        d_ = yaml_parser.YAMLMetaWorkflow(d).to_json(
                            submission_centers=["hms-dbmi"],
                            consortia=["cgap-test", "cgap-core"],
                            version='v1.0.0'
                        )
        # check
        assert d_ == res

def test_metaworkflow_error():
    """
    """

    for i, fn in enumerate(glob.glob('tests/repo_error/portal_objects/metaworkflows/*.yaml')):
        for d in yaml_parser.load_yaml(fn):
            try:
                d_ = yaml_parser.YAMLMetaWorkflow(d).to_json(
                                    submission_centers=["hms-dbmi"],
                                    consortia=["cgap-core"],
                                    version='v1.0.0'
                                )
            except yaml_parser.ValidationError as e:
                pass
