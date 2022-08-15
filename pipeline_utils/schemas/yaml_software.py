yaml_software_schema = {
    ## Schema #########################
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': '/schemas/YAMLSoftware',
    'title': 'YAMLSoftware',
    'description': 'Schema to validate a YAML description of a Software',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'Name of the Software',
            'type': 'string'
        },
        'title': {
            'description': 'Title of the Software',
            'type': 'string'
        },
        'source_url': {
            'description': 'Source url of the Software',
            'type': 'string',
            'format': 'uri',
            'pattern': '^https?\:.+'
        },
        'description': {
            'description': 'Description of the Software',
            'type': 'string'
        },
        'version': {
            'description': 'Version of the Software',
            'type': 'string'
        },
        'commit': {
            'description': 'Commit of the Software',
            'type': 'string'
        }
    },
    'required': ['name'],
    'oneOf': [
        {'required': ['version']},
        {'required': ['commit']}
    ]
}
