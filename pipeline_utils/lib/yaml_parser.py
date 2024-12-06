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


###############################################################
#   Schemas
###############################################################
from pipeline_utils.schemas.yaml_workflow import yaml_workflow_schema
from pipeline_utils.schemas.yaml_metaworkflow import yaml_metaworkflow_schema
from pipeline_utils.schemas.yaml_software import yaml_software_schema
from pipeline_utils.schemas.yaml_reference_file import yaml_reference_file_schema
from pipeline_utils.schemas.yaml_file_format import yaml_file_format_schema
from pipeline_utils.schemas.yaml_reference_genome import yaml_reference_genome_schema


###############################################################
#   Functions
###############################################################
def load_yaml(file):
    """Return a generator to YAML documents in file.
    """
    with open(file) as stream:
        try:
            for d in yaml.safe_load_all(stream):
                yield d
        except yaml.YAMLError as exc:
            sys.exit(exc)

def peek(iterable):
    """Function to check if an iterable is empty.
    If not empty return the complete iterator, else return None.
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
    """Custom Exception for error tracking in schema validation.
    """

    def __init__(self, errors):
        """Constructor method.

            :param errors: Errors from jsonschema.Validator.iter_errors()
            :type errors: Iterable[jsonschema.exceptions.ValidationError]
        """
        errors, errors_ = itertools.tee(errors)
        super().__init__(self._message(errors))
        self.errors = errors_

    def _message(self, errors):
        """Helper to create error message.
        """
        message = 'YAML object failed schema validation.\n'
        for error in errors:
            message += 'ValidationError [{0}]: {1} in path={2}, schema={3}\n'.format(
                            error.validator,
                            error.message,
                            error.relative_path,
                            error.schema
                            )
        return message

###############################################################
#   YAMLTemplate
###############################################################
class YAMLTemplate(object):
    """Template class to work with YAML documents representing pipeline components.
    """

    # schema constants
    NAME_SCHEMA = 'name'
    TITLE_SCHEMA = 'title'
    DESCRIPTION_SCHEMA = 'description'
    CATEGORY_SCHEMA = 'category'
    ALIASES_SCHEMA = 'aliases'
    CONSORTIA_SCHEMA = 'consortia'
    SUBMISSION_CENTERS_SCHEMA = 'submission_centers'
    VERSION_SCHEMA = 'version'
    ACCESSION_SCHEMA = 'accession'
    UUID_SCHEMA = 'uuid'
    ARGUMENT_TYPE_SCHEMA = 'argument_type'
    ARGUMENT_FORMAT_SCHEMA = 'argument_format'
    ARGUMENT_NAME_SCHEMA = 'argument_name'
    VALUE_TYPE_SCHEMA = 'value_type'
    VALUE_SCHEMA = 'value'
    WORKFLOW_ARGUMENT_NAME_SCHEMA = 'workflow_argument_name'
    INPUT_SCHEMA = 'input'
    STATUS_SCHEMA = 'status'
    SECONDARY_FILES_SCHEMA = 'secondary_files'
    SECONDARY_FORMATS_SCHEMA = 'secondary_formats'
    FILE_FORMAT_SCHEMA = 'file_format'
    SECONDARY_FILE_FORMATS_SCHEMA = 'secondary_file_formats'
    FILE_SCHEMA = 'file'
    FILES_SCHEMA = 'files'
    PARAMETER_SCHEMA = 'parameter'
    LICENSE_SCHEMA = 'license'
    WORKFLOW_TYPE_SCHEMA = 'Workflow'
    METAWORKFLOW_TYPE_SCHEMA = 'MetaWorkflow'
    FILEFORMAT_TYPE_SCHEMA = 'FileFormat'
    REFERENCEFILE_TYPE_SCHEMA = 'ReferenceFile'
    REFERENCEGENOME_TYPE_SCHEMA = 'ReferenceGenome'
    SOFTWARE_TYPE_SCHEMA = 'Software'
    VARIANT_TYPE_SCHEMA = "variant_type"
    CODE_SCHEMA = 'code'
    IDENTIFIER_SCHEMA = 'identifier'

    def __init__(self, data, schema):
        """Constructor method.
        """
        self.data = data
        self.schema = schema

    def _validate(self):
        """Helper to validate the document against schema.
        """
        draft202012validator = Draft202012Validator(self.schema)
        errors = draft202012validator.iter_errors(self.data)
        errors_ = peek(errors)
        if errors_:
            raise ValidationError(errors_)

    def _clean_newline(self, line):
        """Helper to clean multiline docstrings from YAML block style indicator "|".
        """
        if ' |' in line:
            line = line.replace(' |', '')
        elif '|' in line:
            line = line.replace('|', '')
        return line

    def _link_title(self, name, version=None):
        """Helper to create a "title" field.
        """
        title = getattr(self, self.TITLE_SCHEMA, None)
        if title:
            if version:
                if version in title:
                    return title
                else:
                    return f'{title} [{version}]'
            else:
                return title
        else:
            if version:
                return f'{name.replace("_", " ")} [{version}]'
            else:
                return f'{name.replace("_", " ")}'

    def _string_consortia(self, consortia):
        """Helper to create a string from "consortia" field.
        """
        return '_'.join(sorted(consortia))

###############################################################
#   YAMLWorkflow, YAML Workflow
###############################################################
class YAMLWorkflow(YAMLTemplate):
    """Class to work with YAML documents representing Workflow objects.
    """

    # schema constants
    INPUT_FILE_SCHEMA = 'Input file'
    OUTPUT_PROCESSED_FILE_SCHEMA = 'Output processed file'
    GENERIC_QC_FILE_SCHEMA = 'Generic QC file'
    OUTPUT_REPORT_FILE_SCHEMA = 'Output report file'
    QC_RULESET_SCHEMA = 'qc_ruleset'
    QC_RULESET_PORTAL_SCHEMA = 'QC ruleset'
    QC_SCHEMA = 'qc'
    REPORT_SCHEMA = 'report'
    ARGUMENT_TO_BE_ATTACHED_TO_SCHEMA = 'argument_to_be_attached_to'
    ZIPPED_SCHEMA = 'zipped'
    JSON_SCHEMA = 'json'
    SOFTWARE_SCHEMA = 'software'
    ARGUMENTS_SCHEMA = 'arguments'
    QC_ZIPPED_SCHEMA = 'qc_zipped'
    QC_JSON_SCHEMA = 'qc_json'

    def __init__(self, data):
        """Constructor method.
        """
        super().__init__(data, yaml_workflow_schema)
        # validate data with schema
        self._validate()
        # load attributes
        for key, val in data.items():
            if key in [self.DESCRIPTION_SCHEMA]:
                val = self._clean_newline(val)
            setattr(self, key, val)

    def _arguments_input(self):
        """Helper to parse input arguments and map to expected JSON structure.
        """
        arguments = []
        for name, values in self.input.items():
            type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            if type == self.FILE_SCHEMA:
                argument_type = self.INPUT_FILE_SCHEMA
            elif type == self.PARAMETER_SCHEMA:
                argument_type = self.PARAMETER_SCHEMA
            elif type == self.QC_RULESET_SCHEMA:
                argument_type = self.QC_RULESET_PORTAL_SCHEMA
            argument_ = {
                self.ARGUMENT_TYPE_SCHEMA: argument_type,
                self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name
                }
            # add format to file argument, TODO
            #   this can be improved in schema to handle a list of formats so no placeholder is needed
            if type == self.FILE_SCHEMA and format not in ['any']:
                # handle format placeholders,
                #   if format is not a placeholder add format field to argument
                argument_[self.ARGUMENT_FORMAT_SCHEMA] = format
            arguments.append(argument_)

        return arguments

    def _arguments_output(self):
        """Helper to parse output arguments and map to expected JSON structure.
        """
        arguments = []
        for name, values in self.output.items():
            # check if it is a file or qc or report argument
            #   if it is file it has a type and a format
            #       argument_type: file.<format>
            #   if it is qc or report only has type
            #       argument_type: qc | report
            try:
                type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            except ValueError:
                type = values[self.ARGUMENT_TYPE_SCHEMA]
            # create right argument schema according to type
            if type == self.FILE_SCHEMA:
                argument_type = self.OUTPUT_PROCESSED_FILE_SCHEMA
                argument_ = {
                    self.ARGUMENT_FORMAT_SCHEMA: format,
                    self.ARGUMENT_TYPE_SCHEMA: argument_type,
                    self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name
                }
                # check for secondary files
                if values.get(self.SECONDARY_FILES_SCHEMA):
                    argument_[self.SECONDARY_FILE_FORMATS_SCHEMA] = values.get(self.SECONDARY_FILES_SCHEMA)
            elif type == self.QC_SCHEMA:
                argument_type = self.GENERIC_QC_FILE_SCHEMA
                # create base QC argument
                argument_ = {
                    self.ARGUMENT_TYPE_SCHEMA: argument_type,
                    self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name,
                    self.ARGUMENT_TO_BE_ATTACHED_TO_SCHEMA: values[self.ARGUMENT_TO_BE_ATTACHED_TO_SCHEMA],
                    self.QC_ZIPPED_SCHEMA: values.get(self.ZIPPED_SCHEMA, False),
                    self.QC_JSON_SCHEMA: values.get(self.JSON_SCHEMA, False),
                }
                # check if it is json or zip
                if argument_[self.QC_JSON_SCHEMA]:
                    argument_[self.ARGUMENT_FORMAT_SCHEMA] = 'json'
                else:
                    argument_[self.ARGUMENT_FORMAT_SCHEMA] = 'zip'
            elif type == self.REPORT_SCHEMA:
                argument_type = self.OUTPUT_REPORT_FILE_SCHEMA
                argument_ = {
                    self.ARGUMENT_TYPE_SCHEMA: argument_type,
                    self.WORKFLOW_ARGUMENT_NAME_SCHEMA: name
                }
            arguments.append(argument_)

        return arguments

    def to_json(
               self,
               version,
               submission_centers, # alias list
               consortia, # alias list
               wflbucket_url
               ):
        """Function to build the corresponding object in JSON format.
        """
        wfl_json = {}

        # common metadata
        wfl_json[self.VERSION_SCHEMA] = version # version
        wfl_json[self.NAME_SCHEMA] = self.name
        wfl_json[self.TITLE_SCHEMA] = self._link_title(self.name, version)
        wfl_json[self.ALIASES_SCHEMA] = [f'{self._string_consortia(consortia)}:{self.WORKFLOW_TYPE_SCHEMA}-{self.name}_{version}']
        wfl_json[self.CATEGORY_SCHEMA] = self.category
        wfl_json[self.SUBMISSION_CENTERS_SCHEMA] = submission_centers
        wfl_json[self.CONSORTIA_SCHEMA] = consortia
        wfl_json[self.DESCRIPTION_SCHEMA] = self.description
        # check if software
        if getattr(self, self.SOFTWARE_SCHEMA, None):
            wfl_json[self.SOFTWARE_SCHEMA] = [f'{self._string_consortia(consortia)}:{self.SOFTWARE_TYPE_SCHEMA}-{s.replace("@", "_")}' for s in getattr(self, self.SOFTWARE_SCHEMA)]
        wfl_json[self.ARGUMENTS_SCHEMA] = self._arguments_input() + self._arguments_output()

        # workflow language and description files
        wfl_json['language'] = self.runner['language'].upper()
        wfl_json['directory_url'] = wflbucket_url
        wfl_json['main_file_name'] = self.runner['main']
        # check if child description files
        if self.runner.get('child'):
            wfl_json['child_file_names'] = self.runner.get('child')

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
    """Class to work with YAML documents representing MetaWorkflow objects.
    """

    # schema constants
    DIMENSION_SCHEMA = 'dimension'
    WORKFLOW_SCHEMA = 'workflow'
    WORKFLOWS_SCHEMA = 'workflows'
    CUSTOM_PF_FIELDS_SCHEMA = 'custom_pf_fields'
    OUTPUT_SCHEMA = 'output'
    CONFIG_SCHEMA = 'config'
    DEPENDENCIES_SCHEMA = 'dependencies'
    SHARDS_SCHEMA = 'shards'
    QC_THRESHOLDS_SCHEMA = 'qc_thresholds'
    OVERALL_QUALITY_STATUS_RULE_SCHEMA = 'overall_quality_status_rule'
    ID_SCHEMA = 'id'
    METRIC_SCHEMA = 'metric'
    OPERATOR_SCHEMA = 'operator'
    PASS_TARGET_SCHEMA = 'pass_target'
    WARN_TARGET_SCHEMA = 'warn_target'
    USE_AS_QC_FLAG_SCHEMA = 'use_as_qc_flag'
    RULE_SCHEMA = 'rule'
    FLAG_SCHEMA = 'flag'
    QC_RULE_SCHEMA = 'qc_rule'
    QC_RULESET_SCHEMA = 'qc_ruleset'
    QC_RULESET_PORTAL_SCHEMA = 'QC ruleset'

    def __init__(self, data):
        """Constructor method.
        """
        super().__init__(data, yaml_metaworkflow_schema)
        # validate data with schema
        self._validate()
        # load attributes
        for key, val in data.items():
            if key in [self.DESCRIPTION_SCHEMA]:
                val = self._clean_newline(val)
            setattr(self, key, val)

    def _arguments(self, input, consortia):
        """Helper to parse arguments and map to expected JSON structure.
        """
        arguments = []
        for name, values in input.items():
            type, format = values[self.ARGUMENT_TYPE_SCHEMA].split('.')
            argument_ = {
                self.ARGUMENT_NAME_SCHEMA: name,
                self.ARGUMENT_TYPE_SCHEMA: type
            }
            if type == self.QC_RULESET_SCHEMA: # replacing qc_ruleset
                                               # with portal correspoding key
                argument_[self.ARGUMENT_TYPE_SCHEMA] = self.QC_RULESET_PORTAL_SCHEMA
            if type == self.PARAMETER_SCHEMA:
                argument_[self.VALUE_TYPE_SCHEMA] = format
            for k, v in values.items():
                if k not in [self.ARGUMENT_TYPE_SCHEMA, self.QC_RULE_SCHEMA]:
                    # handle files specifications, TODO
                    #   this system could be improved in how the schema works and deals with types
                    #
                    #   need to go from file name to dictionary of alias and dimension
                    #    files:
                    #        - foo@v1
                    #   ----- or -------
                    #        - foo@v1
                    #        - bar@v3
                    #   need to convert to:
                    #    files: [
                    #        {file: '<consortia>:ReferenceFile-foo_v1'}
                    #       ]
                    #   ----- or -------
                    #    files: [
                    #        {file: '<consortia>:ReferenceFile-foo_v1', dimension: '0'},
                    #        {file: '<consortia>:ReferenceFile-bar_v3', dimension: '1'}
                    #       ]
                    if k == self.FILES_SCHEMA:
                        v_ = []
                        for i, name_ in enumerate(v):
                            v_.append({self.FILE_SCHEMA: f'{self._string_consortia(consortia)}:{self.REFERENCEFILE_TYPE_SCHEMA}-{name_.replace("@", "_")}',
                                       self.DIMENSION_SCHEMA: str(i)})
                        # remove DIMENSION_SCHEMA field if only one file
                        #   this is necessary so the file will be posted as a string and not a list
                        #   having a list will break tibanna creating the correct input for cwltool
                        if len(v_) == 1:
                            del v_[0][self.DIMENSION_SCHEMA]
                        argument_.setdefault(k, v_)
                    elif k == self.QC_THRESHOLDS_SCHEMA:
                        v_ = {
                            self.QC_THRESHOLDS_SCHEMA: [],
                            self.OVERALL_QUALITY_STATUS_RULE_SCHEMA: values[self.QC_RULE_SCHEMA]
                        }
                        for id, rule in v.items():
                            metric, operator, pass_target, warn_target = rule[self.RULE_SCHEMA].split('|')
                            flag = rule.get(self.FLAG_SCHEMA)
                            # convert to float if number
                            try: pass_target = float(pass_target)
                            except ValueError: pass
                            try: warn_target = float(warn_target)
                            except ValueError: pass
                            # format rule
                            rule_ = {
                                self.ID_SCHEMA: id,
                                self.METRIC_SCHEMA: metric,
                                self.OPERATOR_SCHEMA: operator,
                                self.PASS_TARGET_SCHEMA: pass_target,
                                self.WARN_TARGET_SCHEMA: warn_target
                            }
                            if flag: # add use as flag if present
                                rule_[self.USE_AS_QC_FLAG_SCHEMA] = flag
                            v_[self.QC_THRESHOLDS_SCHEMA].append(rule_)
                        argument_.setdefault(self.VALUE_SCHEMA, v_)
                    else:
                        argument_.setdefault(k, v)
            arguments.append(argument_)

        return arguments

    def _workflows(self, version, consortia):
        """Helper to parse workflow definitions and map to expected JSON structure.
        """
        workflows = []
        for name, values in self.workflows.items():
            # check if lock version
            #   if not use default version
            if values.get(self.VERSION_SCHEMA):
                version_ = values[self.VERSION_SCHEMA]
            else:
                version_ = version
            # basic JSON workflow structure
            workflow_ = {
                self.NAME_SCHEMA: name,
                self.WORKFLOW_SCHEMA: f'{self._string_consortia(consortia)}:{self.WORKFLOW_TYPE_SCHEMA}-{name.split("@")[0]}_{version_}',
                                      # remove unique tag after @ to create the right alias to link
                self.INPUT_SCHEMA: self._arguments(values[self.INPUT_SCHEMA], consortia),
                self.CONFIG_SCHEMA: values[self.CONFIG_SCHEMA]
            }
            # file output can be optional
            #   QC workflows don't always have a file output
            if values.get(self.OUTPUT_SCHEMA):
                workflow_[self.CUSTOM_PF_FIELDS_SCHEMA] = values[self.OUTPUT_SCHEMA]
            # hard dependencies
            if values.get(self.DEPENDENCIES_SCHEMA):
                workflow_[self.DEPENDENCIES_SCHEMA] = values[self.DEPENDENCIES_SCHEMA]
            # fixed shards
            if values.get(self.SHARDS_SCHEMA):
                workflow_[self.SHARDS_SCHEMA] = values[self.SHARDS_SCHEMA]
            workflows.append(workflow_)

        return workflows

    def to_json(
               self,
               version,
               submission_centers, # alias list
               consortia # alias list
               ):
        """Function to build the corresponding object in JSON format.
        """
        metawfl_json = {}

        # common metadata
        metawfl_json[self.NAME_SCHEMA] = self.name
        metawfl_json[self.VERSION_SCHEMA] = version # version
        metawfl_json[self.TITLE_SCHEMA] = self._link_title(self.name, version)
        metawfl_json[self.ALIASES_SCHEMA] = [f'{self._string_consortia(consortia)}:{self.METAWORKFLOW_TYPE_SCHEMA}-{self.name}_{version}']
        metawfl_json[self.CATEGORY_SCHEMA] = self.category
        metawfl_json[self.SUBMISSION_CENTERS_SCHEMA] = submission_centers
        metawfl_json[self.CONSORTIA_SCHEMA] = consortia
        metawfl_json[self.DESCRIPTION_SCHEMA] = self.description
        metawfl_json[self.INPUT_SCHEMA] = self._arguments(self.input, consortia)
        metawfl_json[self.WORKFLOWS_SCHEMA] = self._workflows(version, consortia)

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
    """Class to work with YAML documents representing Software objects.
    """

    # schema constants
    COMMIT_SCHEMA = 'commit'
    SOURCE_URL_SCHEMA = 'source_url'

    def __init__(self, data):
        """Constructor method.
        """
        super().__init__(data, yaml_software_schema)
        # validate data with schema
        self._validate()
        # load attributes
        for key, val in data.items():
            if key in [self.DESCRIPTION_SCHEMA]:
                val = self._clean_newline(val)
            setattr(self, key, val)

    def to_json(
               self,
               submission_centers, # alias list
               consortia # alias list
               ):
        """Function to build the corresponding object in JSON format.
        """
        sftwr_json, version = {}, None

        # common metadata
        sftwr_json[self.NAME_SCHEMA] = self.name
        sftwr_json[self.SUBMISSION_CENTERS_SCHEMA] = submission_centers
        sftwr_json[self.CONSORTIA_SCHEMA] = consortia
        sftwr_json[self.CATEGORY_SCHEMA] = self.category

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

        sftwr_json[self.TITLE_SCHEMA] = self._link_title(self.name)
        sftwr_json[self.ALIASES_SCHEMA] = [f'{self._string_consortia(consortia)}:{self.SOFTWARE_TYPE_SCHEMA}-{self.name}_{version}']

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            sftwr_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            sftwr_json[self.ACCESSION_SCHEMA] = self.accession

        # license
        if getattr(self, self.LICENSE_SCHEMA, None):
            sftwr_json[self.LICENSE_SCHEMA] = self.license

        # code
        if getattr(self, self.CODE_SCHEMA, None):
            sftwr_json[self.CODE_SCHEMA] = self.code

        return sftwr_json


###############################################################
#   YAMLReferenceFile, YAML ReferenceFile
###############################################################
class YAMLReferenceFile(YAMLTemplate):
    """Class to work with YAML documents representing ReferenceFile objects.
    """

    # schema constants
    EXTRA_FILES_SCHEMA = 'extra_files'
    DATA_CATEGORY_SCHEMA = 'data_category'
    DATA_TYPE_SCHEMA = 'data_type'

    def __init__(self, data):
        """Constructor method.
        """
        super().__init__(data, yaml_reference_file_schema)
        # validate data with schema
        self._validate()
        # load attributes
        for key, val in data.items():
            if key in [self.DESCRIPTION_SCHEMA]:
                val = self._clean_newline(val)
            setattr(self, key, val)

    def to_json(
               self,
               submission_centers, # alias list
               consortia # alias list
               ):
        """Function to build the corresponding object in JSON format.
        """
        ref_json = {}

        # common metadata
        ref_json[self.SUBMISSION_CENTERS_SCHEMA] = submission_centers
        ref_json[self.CONSORTIA_SCHEMA] = consortia
        ref_json[self.DESCRIPTION_SCHEMA] = self.description
        ref_json[self.FILE_FORMAT_SCHEMA] = self.format
        ref_json[self.ALIASES_SCHEMA] = [f'{self._string_consortia(consortia)}:{self.REFERENCEFILE_TYPE_SCHEMA}-{self.name}_{self.version}']
        # check for secondary files
        if getattr(self, self.SECONDARY_FILES_SCHEMA, None):
            ref_json[self.EXTRA_FILES_SCHEMA] = getattr(self, self.SECONDARY_FILES_SCHEMA)
        ref_json[self.STATUS_SCHEMA] = getattr(self, self.STATUS_SCHEMA, None) # this will be used during post/patch,
                                                           # if None:
                                                           #    - leave it as is if patch
                                                           #    - set to uploading if post
        ref_json[self.DATA_CATEGORY_SCHEMA] = self.category
        ref_json[self.DATA_TYPE_SCHEMA] = self.type
        # variant_type
        if getattr(self, self.VARIANT_TYPE_SCHEMA, None):
            ref_json[self.VARIANT_TYPE_SCHEMA] = self.variant_type

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            ref_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            ref_json[self.ACCESSION_SCHEMA] = self.accession

        # license
        if getattr(self, self.LICENSE_SCHEMA, None):
            ref_json[self.LICENSE_SCHEMA] = self.license

        # code
        if getattr(self, self.CODE_SCHEMA, None):
            ref_json[self.CODE_SCHEMA] = self.code

        # title
        ref_json[self.TITLE_SCHEMA] = self._link_title(self.name)

        # version
        ref_json[self.VERSION_SCHEMA] = self.version

        return ref_json


###############################################################
#   YAMLFileFormat, YAML FileFormat
###############################################################
class YAMLFileFormat(YAMLTemplate):
    """Class to work with YAML documents representing FileFormat objects.
    """

    # schema constants
    STANDARD_FILE_EXTENSION_SCHEMA = 'standard_file_extension'
    VALID_ITEM_TYPES_SCHEMA = 'valid_item_types'
    EXTRA_FILE_FORMATS_SCHEMA = 'extra_file_formats'
    FILE_TYPES_SCHEMA = 'file_types'

    def __init__(self, data):
        """Constructor method.
        """
        super().__init__(data, yaml_file_format_schema)
        # validate data with schema
        self._validate()
        # load attributes
        for key, val in data.items():
            if key in [self.DESCRIPTION_SCHEMA]:
                val = self._clean_newline(val)
            setattr(self, key, val)

    def to_json(
               self,
               submission_centers, # alias list
               consortia # alias list
               ):
        """Function to build the corresponding object in JSON format.
        """
        frmt_json = {}

        # common metadata
        frmt_json[self.IDENTIFIER_SCHEMA] = self.name
        frmt_json[self.ALIASES_SCHEMA] = [f'{self._string_consortia(consortia)}:{self.FILEFORMAT_TYPE_SCHEMA}-{self.name}']
        frmt_json[self.SUBMISSION_CENTERS_SCHEMA] = submission_centers
        frmt_json[self.CONSORTIA_SCHEMA] = consortia
        frmt_json[self.DESCRIPTION_SCHEMA] = self.description
        frmt_json[self.STANDARD_FILE_EXTENSION_SCHEMA] = self.extension
        frmt_json[self.VALID_ITEM_TYPES_SCHEMA] = getattr(self, self.FILE_TYPES_SCHEMA, ['ReferenceFile', 'OutputFile'])
        # check for secondary formats
        if getattr(self, self.SECONDARY_FORMATS_SCHEMA, None):
            frmt_json[self.EXTRA_FILE_FORMATS_SCHEMA] = getattr(self, self.SECONDARY_FORMATS_SCHEMA)
        frmt_json[self.STATUS_SCHEMA] = getattr(self, self.STATUS_SCHEMA, 'released')

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            frmt_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            frmt_json[self.ACCESSION_SCHEMA] = self.accession

        return frmt_json

###############################################################
#   YAMLReferenceGenome, YAML ReferenceGenome
###############################################################
class YAMLReferenceGenome(YAMLTemplate):
    """Class to work with YAML documents representing ReferenceGenome objects.
    """

    def __init__(self, data):
        """Constructor method.
        """
        super().__init__(data, yaml_reference_genome_schema)
        # validate data with schema
        self._validate()
        # load attributes
        for key, val in data.items():
            setattr(self, key, val)

    def to_json(
               self,
               submission_centers, # alias list
               consortia # alias list
               ):
        """Function to build the corresponding object in JSON format.
        """
        gen_json = {}

        # common metadata
        gen_json[self.IDENTIFIER_SCHEMA] = self.name
        gen_json[self.ALIASES_SCHEMA] = [f'{self._string_consortia(consortia)}:{self.REFERENCEGENOME_TYPE_SCHEMA}-{self.name}_{self.version}']
        gen_json[self.SUBMISSION_CENTERS_SCHEMA] = submission_centers
        gen_json[self.CONSORTIA_SCHEMA] = consortia
        gen_json[self.TITLE_SCHEMA] = self._link_title(self.name, self.version)
        gen_json[self.CODE_SCHEMA] = self.code

        # uuid, accession if specified
        if getattr(self, self.UUID_SCHEMA, None):
            gen_json[self.UUID_SCHEMA] = self.uuid
        if getattr(self, self.ACCESSION_SCHEMA, None):
            gen_json[self.ACCESSION_SCHEMA] = self.accession

        # check linked files
        if getattr(self, self.FILES_SCHEMA, None):
            gen_json[self.FILES_SCHEMA] = []
            for file in self.files:
                gen_json[self.FILES_SCHEMA].append(
                    f'{self._string_consortia(consortia)}:{self.REFERENCEFILE_TYPE_SCHEMA}-{file.replace("@", "_")}')

        return gen_json
