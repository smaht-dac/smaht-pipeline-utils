YamlFrmt_schema = {
    ## Schema #########################
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': '/schemas/YamlFrmt',
    'title': 'YamlFrmt',
    'description': 'Schema to validate a Yaml description of a FileFormat',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'Name of the FileFormat',
            'type': 'string'
        },
        'description': {
            'description': 'Description of the FileFormat',
            'type': 'string'
        },
        'extension': {
            'description': 'Extension of the FileFormat',
            'type': 'string'
        },
        'file_types': {
            'description': 'File types that can use the FileFormat',
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': 'FileReference|FileProcessed'
            }
        },
        'status': {
            'type': 'string'
        },
        'secondary_formats': {
            'description': 'Secondary formats available for the FileFormat',
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }
    },
    'required': ['name', 'description', 'extension']
}
