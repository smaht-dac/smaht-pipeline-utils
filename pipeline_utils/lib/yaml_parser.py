#!/usr/bin/env python

import yaml


###############################################################
#   Functions
###############################################################
def load_yaml(file):
    """
        return a generator to loaded yaml documents in file
    """
    with open(file) as stream:
        try:
            for d in yaml.safe_load_all(stream):
                yield d
        except yaml.YAMLError as exc:
            sys.exit(exc)


###############################################################
#   YamlWfl, Yaml Workflow
###############################################################
class YamlWfl(object):

    def __init__(self, yaml_d):
        """
        """
        for key, val in yaml_d.items():
            setattr(self, key, val)
        self._validate()

    def _validate(self):
        """
        """
        try:
            getattr(self, 'name')
            getattr(self, 'description')
            getattr(self, 'runner')
            getattr(self, 'input')
            getattr(self, 'output')
        except AttributeError as e:
            raise ValueError('JSON validation error, {0}\n'
                                .format(e.args[0]))

    def _arguments_input(self):
        """
        """
        arguments = []
        for name, values in self.input.items():
            type, format = values['argument_type'].split('.')
            if type == 'file':
                argument_type = 'Input file'
            elif type == 'parameter':
                argument_type = 'parameter'
            argument_ = {
                'argument_type': argument_type,
                'workflow_argument_name': name
                }
            arguments.append(argument_)

        return arguments

    def _arguments_output(self):
        """
        """
        arguments = []
        for name, values in self.output.items():
            type, format = values['argument_type'].split('.')
            if type == 'file':
                argument_type = 'Output processed file'
                argument_ = {
                    'argument_format': format,
                    'argument_type': argument_type,
                    'workflow_argument_name': name,
                    'secondary_file_formats': values.get('secondary_files', [])
                }
            elif type == 'qc':
                argument_type = 'Output QC file'
                argument_ = {
                    'argument_type': argument_type,
                    'workflow_argument_name': name,
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
        wfl_json['name'] = self.name + '_' + VERSION
        wfl_json['title'] = getattr(self, 'title', self.name.replace('_', ' ')) + ', ' + VERSION
        wfl_json['aliases'] = [PROJECT + ':' + wfl_json['name']]
        wfl_json['institution'] = '/institutions/' + INSTITUTION + '/'
        wfl_json['project'] = '/projects/' + PROJECT + '/'
        wfl_json['description'] = self.description
        wfl_json['software'] = getattr(self, 'software', [])
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

        return wfl_json


###############################################################
#   YamlMWfl, Yaml MetaWorkflow
###############################################################
class YamlMWfl(object):

    def __init__(self, yaml_d):
        """
        """
        for key, val in yaml_d.items():
            setattr(self, key, val)
        self._validate()

    def _validate(self):
        """
        """
        try:
            getattr(self, 'name')
            getattr(self, 'description')
            getattr(self, 'input')
            getattr(self, 'workflows')
        except AttributeError as e:
            raise ValueError('JSON validation error, {0}\n'
                                .format(e.args[0]))

    def _arguments(self, input):
        """
        """
        arguments = []
        for name, values in input.items():
            type, format = values['argument_type'].split('.')
            argument_ = {
                'argument_name': name,
                'argument_type': type
            }
            if type == 'parameter':
                argument_.setdefault('value_type', format)
            for k, v in values.items():
                if k != 'argument_type':
                    argument_.setdefault(k, v)
            arguments.append(argument_)

        return arguments

    def _workflows(self, VERSION, PROJECT):
        """
        """
        workflows = []
        for name, values in self.workflows.items():
            workflow_ = {
                'name': name,
                'workflow': PROJECT + ':' + name + '_' + VERSION,
                'input': self._arguments(values['input']),
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
        metawfl_json['name'] = self.name
        metawfl_json['version'] = VERSION # version
        metawfl_json['title'] = getattr(self, 'title', self.name.replace('_', ' ')) + ', ' + VERSION
        metawfl_json['aliases'] = [PROJECT + ':' + self.name + '_' + VERSION]
        metawfl_json['institution'] = '/institutions/' + INSTITUTION + '/'
        metawfl_json['project'] = '/projects/' + PROJECT + '/'
        metawfl_json['description'] = self.description
        metawfl_json['input'] = self._arguments(self.input)
        metawfl_json['workflows'] = self._workflows(VERSION, PROJECT)

        return metawfl_json


###############################################################
#   YamlSftwr, Yaml Software
###############################################################
class YamlSftwr(object):

    def __init__(self, yaml_d):
        """
        """
        for key, val in yaml_d.items():
            setattr(self, key, val)
        self._validate()

    def _validate(self):
        """
        """
        try:
            getattr(self, 'name')
        except AttributeError as e:
            raise ValueError('JSON validation error, {0}\n'
                                .format(e.args[0]))

        if not getattr(self, 'version', None):
            if not getattr(self, 'commit', None):
                raise ValueError('JSON validation error, please provide version or commit information\n')

    def to_json(
               self,
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               ):
        """
        """
        sftwr_json, version = {}, None

        # common metadata
        sftwr_json['name'] = self.name
        sftwr_json['institution'] = '/institutions/' + INSTITUTION + '/'
        sftwr_json['project'] = '/projects/' + PROJECT + '/'

        if getattr(self, 'version', None):
            sftwr_json['version'] = self.version
            version = self.version
        else:
            sftwr_json['commit'] = self.commit
            version = self.commit

        if getattr(self, 'description', None):
            sftwr_json['description'] = self.description
        if getattr(self, 'source_url', None):
            sftwr_json['source_url'] = self.source_url

        if getattr(self, 'title', None):
            sftwr_json['title'] = self.title
        else:
            sftwr_json['title'] = self.name + ', ' + version

        sftwr_json['aliases'] = [self.name + '_' + version]

        return sftwr_json


###############################################################
#   YamlRef, Yaml FileReference
###############################################################
class YamlRef(object):

    def __init__(self, yaml_d):
        """
        """
        for key, val in yaml_d.items():
            setattr(self, key, val)
        self._validate()

    def _validate(self):
        """
        """
        try:
            getattr(self, 'name')
            getattr(self, 'description')
            getattr(self, 'format') # file_format
            getattr(self, 'version')
        except AttributeError as e:
            raise ValueError('JSON validation error, {0}\n'
                                .format(e.args[0]))

    def to_json(
               self,
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               ):
        """
        """
        ref_json = {}

        # common metadata
        ref_json['institution'] = '/institutions/' + INSTITUTION + '/'
        ref_json['project'] = '/projects/' + PROJECT + '/'
        ref_json['description'] = self.description
        ref_json['file_format'] = self.format
        ref_json['aliases'] = [PROJECT + ':' + self.name + '_' + self.version]
        ref_json['extra_files'] = getattr(self, 'secondary_files', [])
        ref_json['status'] = getattr(self, 'status', None) # this will be used during post/patch,
                                                           # if None:
                                                           #    - leave it as is if patch
                                                           #    - set to uploading if post

        return ref_json


###############################################################
#   YamlFrmt, Yaml Format
###############################################################
class YamlFrmt(object):

    def __init__(self, yaml_d):
        """
        """
        for key, val in yaml_d.items():
            setattr(self, key, val)
        self._validate()

    def _validate(self):
        """
        """
        try:
            getattr(self, 'name')
            getattr(self, 'description')
            getattr(self, 'extension') # standard_file_extension
        except AttributeError as e:
            raise ValueError('JSON validation error, {0}\n'
                                .format(e.args[0]))

    def to_json(
               self,
               INSTITUTION='INSTITUTION', # alias
               PROJECT='PROJECT', # alias
               ):
        """
        """
        frmt_json = {}

        # common metadata
        frmt_json['file_format'] = self.name
        frmt_json['aliases'] = [self.name]
        frmt_json['institution'] = '/institutions/' + INSTITUTION + '/'
        frmt_json['project'] = '/projects/' + PROJECT + '/'
        frmt_json['description'] = self.description
        frmt_json['standard_file_extension'] = self.extension
        frmt_json['valid_item_types'] = getattr(self, 'file_types', ['FileReference', 'FileProcessed'])
        frmt_json['extrafile_formats'] = getattr(self, 'secondary_formats', [])
        frmt_json['status'] = getattr(self, 'status', 'shared')

        return frmt_json
