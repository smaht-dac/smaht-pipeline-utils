YamlWfl_schema = {
    ## Schema #########################
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': '/schemas/YamlWfl',
    'title': 'YamlWfl',
    'description': 'Schema to validate a Yaml description of a Workflow',
    'type': 'object',
    'properties': {

        ## Workflow information #######
        'name': {
            'description': 'Name of the Workflow',
            'type': 'string'
        },
        'title': {
            'description': 'Title of the Workflow',
            'type': 'string'
        },
        'description': {
            'description': 'Description of the Workflow',
            'type': 'string'
        },
        'runner': {
            'description': 'Workflow description in standard language',
            'type': 'object',
            'properties': {
                'language': {
                    'description': 'Language used in Workflow description',
                    'type': 'string',
                    'pattern': '[wW][dD][lL]|[cC][wW][lL]'
                },
                'main': {
                    'description': 'Main description file',
                    'type': 'string',
                    'pattern': '.+\.cwl|.+\.wdl'
                },
                'child': {
                    'description': 'Supplementary description files used by main',
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'pattern': '.+\.cwl|.+\.wdl'
                    }
                }
            },
            'required': ['language', 'main']
        },
        'software': {
            'description': 'List of software used in the Workflow',
            'type': 'array',
            'items': {
                'type': 'string'
            }
        },

        ## Input information ##########
        'input': {
            'description': 'Input files and parameters',
            'type': 'object',
            'patternProperties': {
                '.+': {'$ref': '/schemas/argument'}
            }
        },

        ## Output information #########
        'output': {
            'description': 'Output files and quality controls',
            'type': 'object',
            'patternProperties': {
                '.+': {'$ref': '/schemas/argument'}
            }
        }
    },
    'required': ['name', 'description', 'runner', 'input', 'output'],

    ## Sub-schemas ####################
    '$defs': {
        'argument': {
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': '/schemas/argument',
            'type': 'object',
            'properties': {
                'argument_type': {
                    'type': 'string',
                    'pattern': '^file\..+|^parameter\..+|^qc\..+'
                },
                'secondary_files': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                }
            },
            'required': ['argument_type'],

            ## qc specific ############
            'if': {
                'type': 'object',
                'properties': {
                    'argument_type': {
                        'pattern': '^qc\..+'
                    }
                },
            },
            'then': {
                'properties': {
                    'argument_to_be_attached_to': {
                        'type': 'string'
                    },
                    'zipped': {
                        'type': 'boolean'
                    },
                    'html': {
                        'type': 'boolean'
                    },
                    'json': {
                        'type': 'boolean'
                    },
                    'table': {
                        'type': 'boolean'
                    }
                },
                'required': ['argument_to_be_attached_to']
            },
        }
    }
}
