#################################################################
#   Libraries
#################################################################
import sys, os
import pytest
from jsonschema import Draft202012Validator

###############################################################
#   Schemas
###############################################################
from pipeline_utils.schemas.yaml_workflow import yaml_workflow_schema
from pipeline_utils.schemas.yaml_metaworkflow import yaml_metaworkflow_schema
from pipeline_utils.schemas.yaml_software import yaml_software_schema
from pipeline_utils.schemas.yaml_reference_file import yaml_reference_file_schema
from pipeline_utils.schemas.yaml_file_format import yaml_file_format_schema

###############################################################
#   Tests
###############################################################
def test_check_schema_fail():
    """
    """
    schema_fail = {'type': 1}

    with pytest.raises(Exception) as e_info:
        Draft202012Validator.check_schema(schema_fail)

def test_yaml_file_format_schema():
    """
    """
    Draft202012Validator.check_schema(yaml_file_format_schema)

def test_yaml_reference_file_schema():
    """
    """
    Draft202012Validator.check_schema(yaml_reference_file_schema)

def test_yaml_software_schema():
    """
    """
    Draft202012Validator.check_schema(yaml_software_schema)

def test_yaml_metaworkflow_schema():
    """
    """
    Draft202012Validator.check_schema(yaml_metaworkflow_schema)

def test_yaml_workflow_schema():
    """
    """
    Draft202012Validator.check_schema(yaml_workflow_schema)
