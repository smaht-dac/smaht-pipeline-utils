#!/usr/bin/env python3

###########################################################
#
#   yaml_parser
#      classes to parse portal objects in YAML format
#
#   Michele Berselli - berselli.michele@gmail.com
#
###########################################################

import os, sys
import yaml
import itertools
from jsonschema import Draft202012Validator
import structlog


###############################################################
#   Schemas
###############################################################
from pipeline_utils.schemas.yaml_workflow import yaml_workflow_schema
from pipeline_utils.schemas.yaml_metaworkflow import yaml_metaworkflow_schema
from pipeline_utils.schemas.yaml_software import yaml_software_schema
from pipeline_utils.schemas.yaml_file_reference import yaml_file_reference_schema
from pipeline_utils.schemas.yaml_file_format import yaml_file_format_schema


###############################################################
#   Logger
###############################################################
logger = structlog.getLogger(__name__)


###############################################################
#   Functions
###############################################################
def load_yaml(file):
    """Return a generator to YAML documents in file
    """
    with open(file) as stream:
        try:
            for d in yaml.safe_load_all(stream):
                yield d
        except yaml.YAMLError as exc:
            sys.exit(exc)

def peek(iterable):
    """
    """
    try:
        first = next(iterable)
    except StopIteration:
        return None

    return itertools.chain([first], iterable)


###############################################################
#   SchemaError
###############################################################
class SchemaError(Exception):
    """Custom exception for error tracking
    """

    def __init__(self):
        message = 'YAML object failed schema validation'
        super().__init__(message)


###############################################################
#   YAMLTemplate
###############################################################
class YAMLTemplate(object):
    """
    """

    # Schema constants
    NAME_SCHEMA = 'name'
    TITLE_SCHEMA = 'title'
    DESCRIPTION_SCHEMA = 'description'
    ALIASES_SCHEMA = 'aliases'
    PROJECT_SCHEMA = 'project'
    INSTITUTION_SCHEMA = 'institution'
    VERSION_SCHEMA = 'version'
    ACCESSION_SCHEMA = 'accession'
    UUID_SCHEMA = 'uuid'
    ARGUMENT_TYPE_SCHEMA = 'argument_type'
    ARGUMENT_FORMAT_SCHEMA = 'argument_format'
    ARGUMENT_NAME_SCHEMA = 'argument_name'
    VALUE_TYPE_SCHEMA = 'value_type'
    WORKFLOW_ARGUMENT_NAME_SCHEMA = 'workflow_argument_name'
    INPUT_SCHEMA = 'input'
    STATUS_SCHEMA = 'status'
    SECONDARY_FILES_SCHEMA = 'secondary_files'
    SECONDARY_FORMATS_SCHEMA = 'secondary_formats'
    FILE_FORMAT_SCHEMA = 'file_format'
    SECONDARY_FILE_FORMATS_SCHEMA = 'secondary_file_formats'
    INSTITUTIONS_SCHEMA = 'institutions'
    PROJECTS_SCHEMA = 'projects'

    def __init__(self, data, schema):
        """
        """
        self.data = data
        self.schema = schema

    def _validate(self):
        """
        """
        draft202012validator = Draft202012Validator(self.schema)
        errors = draft202012validator.iter_errors(self.data)
        errors_ = peek(errors)
        if errors_:
            for error in errors_:
                logger.error('{0} Schema Error: {1} in {2}'.format(
                                            error.validator.upper(),
                                            error.message,
                                            ' -> '.join(map(str, error.path))
                                            )
                            )
            raise SchemaError


###############################################################
#   YAMLWorkflow, YAML Workflow
###############################################################
class YAMLWorkflow(YAMLTemplate):

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_workflow_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            setattr(self, key, val)

    def _arguments_input(self):
        """
        """
        arguments = []
        for name, values in self.input.items():
            type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            if type == 'file':
                argument_type = 'Input file'
            elif type == 'parameter':
                argument_type = 'parameter'
            argument_ = {
                self.ARGUMENT_TYPE_SCHEMA: argument_type,
                self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name
                }
            arguments.append(argument_)

        return arguments

    def _arguments_output(self):
        """
        """
        arguments = []
        for name, values in self.output.items():
            type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            if type == 'file':
                argument_type = 'Output processed file'
                argument_ = {
                    self.ARGUMENT_FORMAT_SCHEMA: format,
                    self.ARGUMENT_TYPE_SCHEMA: argument_type,
                    self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name,
                    self.SECONDARY_FILE_FORMATS_SCHEMA: values.get(self.SECONDARY_FILES_SCHEMA, [])
                }
            elif type == 'qc':
                argument_type = 'Output QC file'
                argument_ = {
                    self.ARGUMENT_TYPE_SCHEMA: argument_type,
                    self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name,
                    'argument_to_be_attached_to': values['argument_to_be_attached_to'],
                    'qc_type': format,
                    'qc_zipped': values.get('zipped', False),
                    'qc_html': values.get('html', False),
                    'qc_json': values.get('json', False),
                    'qc_table': values.get('table', False)
                }
            arguments.append(argument_)

        return arguments

    def to_json(
               self,
               VERSION='VERSION',
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               WFLBUCKET_URL='s3://WFLBUCKET/PIPELINE/VERSION',
               ):
        """
        """
        wfl_json = {}

        # common metadata
        wfl_json['app_name'] = self.name # name
        wfl_json['app_version'] = VERSION # version
        wfl_json[self.NAME_SCHEMA] = f'{self.name}_{VERSION}'
        wfl_json[self.TITLE_SCHEMA] = f'{getattr(self, self.TITLE_SCHEMA, self.name.replace("_", " "))}, {VERSION}'
        wfl_json[self.ALIASES_SCHEMA] = [f'{PROJECT}:{wfl_json[self.NAME_SCHEMA]}']
        wfl_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{INSTITUTION}/'
        wfl_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{PROJECT}/'
        wfl_json[self.DESCRIPTION_SCHEMA] = self.description
        wfl_json['software'] = [s.replace('@', '_') for s in getattr(self, 'software', [])]
        wfl_json['arguments'] = self._arguments_input() + self._arguments_output()

        # workflow language
        language = self.runner.get('language')
        if not language or language.lower() == 'cwl':
            wfl_json['cwl_directory_url_v1'] = WFLBUCKET_URL
            wfl_json['cwl_main_filename'] = self.runner['main']
            wfl_json['cwl_child_filenames'] = self.runner.get('child', [])
        elif language.lower() == 'wdl':
            wfl_json['wdl_directory_url'] = WFLBUCKET_URL
            wfl_json['wdl_main_filename'] = self.runner['main']
            wfl_json['wdl_child_filenames'] = self.runner.get('child', [])
            wfl_json['workflow_language'] = 'wdl'

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            wfl_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            wfl_json[self.ACCESSION_SCHEMA] = self.accession

        return wfl_json


###############################################################
#   YAMLMetaWorkflow, YAML MetaWorkflow
###############################################################
class YAMLMetaWorkflow(YAMLTemplate):

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_metaworkflow_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            setattr(self, key, val)

    def _arguments(self, input, PROJECT):
        """
        """
        arguments = []
        for name, values in input.items():
            type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            argument_ = {
                self.ARGUMENT_NAME_SCHEMA: name,
                self.ARGUMENT_TYPE_SCHEMA: type
            }
            if type == 'parameter':
                argument_.setdefault(self.VALUE_TYPE_SCHEMA, format)
            for k, v in values.items():
                if k != self.ARGUMENT_TYPE_SCHEMA:
                    # handle files specifications
                    #   need to go from file name to dictionary of alias and dimension
                    #    files:
                    #        - foo@v1
                    #        - bar@v3
                    #   need to convert to:
                    #    files: [
                    #        {'file': 'PROJECT:foo_v1', 'dimension': '0'},
                    #        {'file': 'PROJECT:bar_v3', 'dimension': '1'}
                    #       ]
                    if k == 'files':
                        v_ = []
                        for i, name_ in enumerate(v):
                            v_.append({'file': f'{PROJECT}:{name_.replace("@", "_")}',
                                       'dimension': str(i)})
                        argument_.setdefault(k, v_)
                    else:
                        argument_.setdefault(k, v)
            arguments.append(argument_)

        return arguments

    def _workflows(self, VERSION, PROJECT):
        """
        """
        workflows = []
        for name, values in self.workflows.items():
            workflow_ = {
                self.NAME_SCHEMA: name,
                'workflow': f'{PROJECT}:{name}_{VERSION}',
                self.INPUT_SCHEMA: self._arguments(values[self.INPUT_SCHEMA], PROJECT),
                'custom_pf_fields': values['output'],
                'config': values['config']
            }
            workflows.append(workflow_)

        return workflows

    def to_json(
               self,
               VERSION='VERSION',
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               ):
        """
        """
        metawfl_json = {}

        # common metadata
        metawfl_json[self.NAME_SCHEMA] = self.name
        metawfl_json[self.VERSION_SCHEMA] = VERSION # version
        metawfl_json[self.TITLE_SCHEMA] = f'{getattr(self, self.TITLE_SCHEMA, self.name.replace("_", " "))}, {VERSION}'
        metawfl_json[self.ALIASES_SCHEMA] = [f'{PROJECT}:{self.name}_{VERSION}']
        metawfl_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{INSTITUTION}/'
        metawfl_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{PROJECT}/'
        metawfl_json[self.DESCRIPTION_SCHEMA] = self.description
        metawfl_json[self.INPUT_SCHEMA] = self._arguments(self.input, PROJECT)
        metawfl_json['workflows'] = self._workflows(VERSION, PROJECT)

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            metawfl_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            metawfl_json[self.ACCESSION_SCHEMA] = self.accession

        return metawfl_json


###############################################################
#   YAMLSoftware, YAML Software
###############################################################
class YAMLSoftware(YAMLTemplate):

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_software_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            setattr(self, key, val)

    def to_json(
               self,
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               ):
        """
        """
        sftwr_json, version = {}, None

        # common metadata
        sftwr_json[self.NAME_SCHEMA] = self.name
        sftwr_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{INSTITUTION}/'
        sftwr_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{PROJECT}/'

        if getattr(self, self.VERSION_SCHEMA, None):
            sftwr_json[self.VERSION_SCHEMA] = self.version
            version = self.version
        else:
            sftwr_json['commit'] = self.commit
            version = self.commit

        if getattr(self, self.DESCRIPTION_SCHEMA, None):
            sftwr_json[self.DESCRIPTION_SCHEMA] = self.description
        if getattr(self, 'source_url', None):
            sftwr_json['source_url'] = self.source_url

        if getattr(self, self.TITLE_SCHEMA, None):
            sftwr_json[self.TITLE_SCHEMA] = self.title
        else:
            sftwr_json[self.TITLE_SCHEMA] = f'{self.name}, {version}'

        sftwr_json[self.ALIASES_SCHEMA] = [f'{self.name}_{version}']

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            sftwr_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            sftwr_json[self.ACCESSION_SCHEMA] = self.accession

        return sftwr_json


###############################################################
#   YAMLFileReference, YAML FileReference
###############################################################
class YAMLFileReference(YAMLTemplate):

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_file_reference_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            setattr(self, key, val)

    def to_json(
               self,
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               ):
        """
        """
        ref_json = {}

        # common metadata
        ref_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{INSTITUTION}/'
        ref_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{PROJECT}/'
        ref_json[self.DESCRIPTION_SCHEMA] = self.description
        ref_json[self.FILE_FORMAT_SCHEMA] = self.format
        ref_json[self.ALIASES_SCHEMA] = [f'{PROJECT}:{self.name}_{self.version}']
        ref_json['extra_files'] = getattr(self, self.SECONDARY_FILES_SCHEMA, [])
        ref_json[self.STATUS_SCHEMA] = getattr(self, self.STATUS_SCHEMA, None) # this will be used during post/patch,
                                                           # if None:
                                                           #    - leave it as is if patch
                                                           #    - set to uploading if post

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            ref_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            ref_json[self.ACCESSION_SCHEMA] = self.accession

        return ref_json


###############################################################
#   YAMLFileFormat, YAML FileFormat
###############################################################
class YAMLFileFormat(YAMLTemplate):

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_file_format_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            setattr(self, key, val)

    def to_json(
               self,
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               ):
        """
        """
        frmt_json = {}

        # common metadata
        frmt_json[self.FILE_FORMAT_SCHEMA] = self.name
        frmt_json[self.ALIASES_SCHEMA] = [self.name]
        frmt_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{INSTITUTION}/'
        frmt_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{PROJECT}/'
        frmt_json[self.DESCRIPTION_SCHEMA] = self.description
        frmt_json['standard_file_extension'] = self.extension
        frmt_json['valid_item_types'] = getattr(self, 'file_types', ['FileReference', 'FileProcessed'])
        frmt_json['extrafile_formats'] = getattr(self, self.SECONDARY_FORMATS_SCHEMA, [])
        frmt_json[self.STATUS_SCHEMA] = getattr(self, self.STATUS_SCHEMA, 'shared')

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            frmt_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            frmt_json[self.ACCESSION_SCHEMA] = self.accession

        return frmt_json
