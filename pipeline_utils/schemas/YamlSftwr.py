YamlSftwr_schema = {
    ## Schema #########################
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': '/schemas/YamlSftwr',
    'title': 'YamlSftwr',
    'description': 'Schema to validate a Yaml description of a Software',
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
