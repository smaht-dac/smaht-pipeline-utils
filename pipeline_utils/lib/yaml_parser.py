#!/usr/bin/env python3

###########################################################
#
#   yaml_parser
#      classes to parse portal objects in YAML format
#
#   Michele Berselli - berselli.michele@gmail.com
#
###########################################################

import sys
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
#   ValidationError
###############################################################
class ValidationError(Exception):
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
    FILE_SCHEMA = 'file'
    FILES_SCHEMA = 'files'
    PARAMETER_SCHEMA = 'parameter'

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
                logger.error('- ValidationError [{0}]: {1} in path={2}, schema={3}'.format(
                                error.validator,
                                error.message,
                                error.relative_path,
                                error.schema
                                )
                            )
            raise ValidationError


###############################################################
#   YAMLWorkflow, YAML Workflow
###############################################################
class YAMLWorkflow(YAMLTemplate):

    # Schema constants
    INPUT_FILE_SCHEMA = 'Input file'
    OUTPUT_PROCESSED_FILE_SCHEMA = 'Output processed file'
    OUTPUT_QC_FILE_SCHEMA = 'Output QC file'
    QC_SCHEMA = 'qc'
    ARGUMENT_TO_BE_ATTACHED_TO_SCHEMA = 'argument_to_be_attached_to'
    ZIPPED_SCHEMA = 'zipped'
    HTML_SCHEMA = 'html'
    JSON_SCHEMA = 'json'
    TABLE_SCHEMA = 'table'
    APP_NAME_SCHEMA = 'app_name'
    APP_VERSION_SCHEMA = 'app_version'
    SOFTWARE_SCHEMA = 'software'
    ARGUMENTS_SCHEMA = 'arguments'
    QC_TYPE_SCHEMA = 'qc_type'
    QC_ZIPPED_SCHEMA = 'qc_zipped'
    QC_HTML_SCHEMA = 'qc_html'
    QC_JSON_SCHEMA = 'qc_json'
    QC_TABLE_SCHEMA = 'qc_table'

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_workflow_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            if ' |' in val:
                val = val.replace(' |', '')
            elif '|' in val:
                val = val.replace('|', '')
            setattr(self, key, val)

    def _arguments_input(self):
        """
        """
        arguments = []
        for name, values in self.input.items():
            type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            if type == self.FILE_SCHEMA:
                argument_type = self.INPUT_FILE_SCHEMA
            elif type == self.PARAMETER_SCHEMA:
                argument_type = self.PARAMETER_SCHEMA
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
            if type == self.FILE_SCHEMA:
                argument_type = self.OUTPUT_PROCESSED_FILE_SCHEMA
                argument_ = {
                    self.ARGUMENT_FORMAT_SCHEMA: format,
                    self.ARGUMENT_TYPE_SCHEMA: argument_type,
                    self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name,
                    self.SECONDARY_FILE_FORMATS_SCHEMA: values.get(self.SECONDARY_FILES_SCHEMA, [])
                }
            elif type == self.QC_SCHEMA:
                argument_type = self.OUTPUT_QC_FILE_SCHEMA
                argument_ = {
                    self.ARGUMENT_TYPE_SCHEMA: argument_type,
                    self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name,
                    self.ARGUMENT_TO_BE_ATTACHED_TO_SCHEMA: values[self.ARGUMENT_TO_BE_ATTACHED_TO_SCHEMA],
                    self.QC_TYPE_SCHEMA: format,
                    self.QC_ZIPPED_SCHEMA: values.get(self.ZIPPED_SCHEMA, False),
                    self.QC_HTML_SCHEMA: values.get(self.HTML_SCHEMA, False),
                    self.QC_JSON_SCHEMA: values.get(self.JSON_SCHEMA, False),
                    self.QC_TABLE_SCHEMA: values.get(self.TABLE_SCHEMA, False)
                }
            arguments.append(argument_)

        return arguments

    def to_json(
               self,
               version='VERSION',
               institution='INSTITUTION', # alias
               project='PROJECT', # alias
               wflbucket_url='s3://WFLBUCKET/PIPELINE/VERSION',
               ):
        """
        """
        wfl_json = {}

        # common metadata
        wfl_json[self.APP_NAME_SCHEMA] = self.name # name
        wfl_json[self.APP_VERSION_SCHEMA] = version # version
        wfl_json[self.NAME_SCHEMA] = f'{self.name}_{version}'
        wfl_json[self.TITLE_SCHEMA] = f'{getattr(self, self.TITLE_SCHEMA, self.name.replace("_", " "))}, {version}'
        wfl_json[self.ALIASES_SCHEMA] = [f'{project}:{wfl_json[self.NAME_SCHEMA]}']
        wfl_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{institution}/'
        wfl_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{project}/'
        wfl_json[self.DESCRIPTION_SCHEMA] = self.description
        wfl_json[self.SOFTWARE_SCHEMA] = [s.replace('@', '_') for s in getattr(self, self.SOFTWARE_SCHEMA, [])]
        wfl_json[self.ARGUMENTS_SCHEMA] = self._arguments_input() + self._arguments_output()

        # workflow language (TODO)
        #   we need to improve tibanna to have a unique general key for this
        language = self.runner.get('language')
        if not language or language.lower() == 'cwl':
            wfl_json['cwl_directory_url_v1'] = wflbucket_url
            wfl_json['cwl_main_filename'] = self.runner['main']
            wfl_json['cwl_child_filenames'] = self.runner.get('child', [])
        elif language.lower() == 'wdl':
            wfl_json['wdl_directory_url'] = wflbucket_url
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

    # Schema constants
    DIMENSION_SCHEMA = 'dimension'
    WORKFLOW_SCHEMA = 'workflow'
    WORKFLOWS_SCHEMA = 'workflows'
    CUSTOM_PF_FIELDS_SCHEMA = 'custom_pf_fields'
    OUTPUT_SCHEMA = 'output'
    CONFIG_SCHEMA = 'config'

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_metaworkflow_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            if ' |' in val:
                val = val.replace(' |', '')
            elif '|' in val:
                val = val.replace('|', '')
            setattr(self, key, val)

    def _arguments(self, input, project):
        """
        """
        arguments = []
        for name, values in input.items():
            type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            argument_ = {
                self.ARGUMENT_NAME_SCHEMA: name,
                self.ARGUMENT_TYPE_SCHEMA: type
            }
            if type == self.PARAMETER_SCHEMA:
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
                    #        {self.FILE_SCHEMA: 'project:foo_v1', self.DIMENSION_SCHEMA: '0'},
                    #        {self.FILE_SCHEMA: 'project:bar_v3', self.DIMENSION_SCHEMA: '1'}
                    #       ]
                    if k == self.FILES_SCHEMA:
                        v_ = []
                        for i, name_ in enumerate(v):
                            v_.append({self.FILE_SCHEMA: f'{project}:{name_.replace("@", "_")}',
                                       self.DIMENSION_SCHEMA: str(i)})
                        argument_.setdefault(k, v_)
                    else:
                        argument_.setdefault(k, v)
            arguments.append(argument_)

        return arguments

    def _workflows(self, version, project):
        """
        """
        workflows = []
        for name, values in self.workflows.items():
            workflow_ = {
                self.NAME_SCHEMA: name,
                self.WORKFLOW_SCHEMA: f'{project}:{name}_{version}',
                self.INPUT_SCHEMA: self._arguments(values[self.INPUT_SCHEMA], project),
                self.CUSTOM_PF_FIELDS_SCHEMA: values[self.OUTPUT_SCHEMA],
                self.CONFIG_SCHEMA: values[self.CONFIG_SCHEMA]
            }
            workflows.append(workflow_)

        return workflows

    def to_json(
               self,
               version='VERSION',
               institution='INSTITUTION', # alias
               project='PROJECT', # alias
               ):
        """
        """
        metawfl_json = {}

        # common metadata
        metawfl_json[self.NAME_SCHEMA] = self.name
        metawfl_json[self.VERSION_SCHEMA] = version # version
        metawfl_json[self.TITLE_SCHEMA] = f'{getattr(self, self.TITLE_SCHEMA, self.name.replace("_", " "))}, {version}'
        metawfl_json[self.ALIASES_SCHEMA] = [f'{project}:{self.name}_{version}']
        metawfl_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{institution}/'
        metawfl_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{project}/'
        metawfl_json[self.DESCRIPTION_SCHEMA] = self.description
        metawfl_json[self.INPUT_SCHEMA] = self._arguments(self.input, project)
        metawfl_json[self.WORKFLOWS_SCHEMA] = self._workflows(version, project)

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

    # Schema constants
    COMMIT_SCHEMA = 'commit'
    SOURCE_URL_SCHEMA = 'source_url'

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_software_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            if ' |' in val:
                val = val.replace(' |', '')
            elif '|' in val:
                val = val.replace('|', '')
            setattr(self, key, val)

    def to_json(
               self,
               institution='INSTITUTION', # alias
               project='PROJECT', # alias
               ):
        """
        """
        sftwr_json, version = {}, None

        # common metadata
        sftwr_json[self.NAME_SCHEMA] = self.name
        sftwr_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{institution}/'
        sftwr_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{project}/'

        if getattr(self, self.VERSION_SCHEMA, None):
            sftwr_json[self.VERSION_SCHEMA] = self.version
            version = self.version
        else:
            sftwr_json[self.COMMIT_SCHEMA] = self.commit
            version = self.commit

        if getattr(self, self.DESCRIPTION_SCHEMA, None):
            sftwr_json[self.DESCRIPTION_SCHEMA] = self.description
        if getattr(self, self.SOURCE_URL_SCHEMA, None):
            sftwr_json[self.SOURCE_URL_SCHEMA] = self.source_url

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

    # Schema constants
    EXTRA_FILES_SCHEMA = 'extra_files'

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_file_reference_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            if ' |' in val:
                val = val.replace(' |', '')
            elif '|' in val:
                val = val.replace('|', '')
            setattr(self, key, val)

    def to_json(
               self,
               institution='INSTITUTION', # alias
               project='PROJECT', # alias
               ):
        """
        """
        ref_json = {}

        # common metadata
        ref_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{institution}/'
        ref_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{project}/'
        ref_json[self.DESCRIPTION_SCHEMA] = self.description
        ref_json[self.FILE_FORMAT_SCHEMA] = self.format
        ref_json[self.ALIASES_SCHEMA] = [f'{project}:{self.name}_{self.version}']
        ref_json[self.EXTRA_FILES_SCHEMA] = getattr(self, self.SECONDARY_FILES_SCHEMA, [])
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

    # Schema constants
    STANDARD_FILE_EXTENSION_SCHEMA = 'standard_file_extension'
    VALID_ITEM_TYPES_SCHEMA = 'valid_item_types'
    EXTRAFILE_FORMATS_SCHEMA = 'extrafile_formats'
    FILE_TYPES_SCHEMA = 'file_types'

    def __init__(self, data):
        """
        """
        super().__init__(data, yaml_file_format_schema)
        # Validate data with schema
        self._validate()
        # Load attributes
        for key, val in data.items():
            if ' |' in val:
                val = val.replace(' |', '')
            elif '|' in val:
                val = val.replace('|', '')
            setattr(self, key, val)

    def to_json(
               self,
               institution='INSTITUTION', # alias
               project='PROJECT', # alias
               ):
        """
        """
        frmt_json = {}

        # common metadata
        frmt_json[self.FILE_FORMAT_SCHEMA] = self.name
        frmt_json[self.ALIASES_SCHEMA] = [self.name]
        frmt_json[self.INSTITUTION_SCHEMA] = f'/{self.INSTITUTIONS_SCHEMA}/{institution}/'
        frmt_json[self.PROJECT_SCHEMA] = f'/{self.PROJECTS_SCHEMA}/{project}/'
        frmt_json[self.DESCRIPTION_SCHEMA] = self.description
        frmt_json[self.STANDARD_FILE_EXTENSION_SCHEMA] = self.extension
        frmt_json[self.VALID_ITEM_TYPES_SCHEMA] = getattr(self, self.FILE_TYPES_SCHEMA, ['FileReference', 'FileProcessed'])
        frmt_json[self.EXTRAFILE_FORMATS_SCHEMA] = getattr(self, self.SECONDARY_FORMATS_SCHEMA, [])
        frmt_json[self.STATUS_SCHEMA] = getattr(self, self.STATUS_SCHEMA, 'shared')

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            frmt_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            frmt_json[self.ACCESSION_SCHEMA] = self.accession

        return frmt_json
