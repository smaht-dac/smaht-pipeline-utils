YamlMWfl_schema = {
    ## Schema #########################
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': '/schemas/YamlMWfl',
    'title': 'YamlMWfl',
    'description': 'Schema to validate a Yaml description of a MetaWorkflow',
    'type': 'object',
    'properties': {

        ## MetaWorkflow information ###
        'name': {
            'description': 'Name of the MetaWorkflow',
            'type': 'string'
        },
        'title': {
            'description': 'Title of the MetaWorkflow',
            'type': 'string'
        },
        'description': {
            'description': 'Description of the MetaWorkflow',
            'type': 'string'
        },

        ## General input information ##
        'input': {
            'description': 'Pipeline input, reference files, and general arguments',
            'type': 'object',
            'patternProperties': {
                '.+': {'$ref': '/schemas/argument'}
            }
        },

        # Workflows information ######
        'workflows': {
            'description': 'Workflows information and their dependencies',
            'type': 'object',
            'patternProperties': {
                '.+': {
                    'description': 'Workflow information',
                    'type': 'object',
                    'properties': {
                        'input': {
                            'description': 'Workflow input and dependencies information',
                            'type': 'object',
                            'patternProperties': {
                                '.+': {'$ref': '/schemas/argument'}
                            }
                        },
                        'output': {
                            'description': 'Workflow output information',
                            'type': 'object',
                            'patternProperties': {
                                '.+': {'$ref': '/schemas/argument-output'}
                            }
                        }
                    },
                    'required': ['input', 'output']
                }
            }
        }
    },
    'required': ['name', 'description', 'input', 'workflows'],

    ## Sub-schemas ####################
    '$defs': {
        'argument': {
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': '/schemas/argument',
            'type': 'object',
            'properties': {
                'argument_type': {
                    'type': 'string',
                    'pattern': '^file\..+|^parameter\..+'
                },
                'dimensionality': {
                    'type': 'number'
                },
                'files': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'pattern': '.+\@.+' # check for <name>@<version>
                    }
                },
                'source': {
                    'type': 'string'
                },
                'source_argument_name': {
                    'type': 'string'
                },
                'scatter': {
                    'type': 'number'
                },
                'gather': {
                    'type': 'number'
                },
                'input_dimension': {
                    'type': 'number'
                },
                'extra_dimension': {
                    'type': 'number'
                },
                'mount': {
                    'type': 'boolean'
                },
                'rename': {
                    'type': 'string',
                    'pattern': '^formula\:.+'
                },
                'unzip': {
                    'type': 'string'
                }
            },
            'required': ['argument_type']
        },
        'argument-output': {
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': '/schemas/argument-output',
            'type': 'object',
            'properties': {
                'description': {
                    'type': 'string'
                },
                'linkto_location': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                },
                'file_type': {
                    'type': 'string'
                },
                'higlass_file': {
                    'type': 'boolean'
                },
                'variant_type': {
                    'type': 'string'
                }
            },
            'required': []
        }
    }
}
