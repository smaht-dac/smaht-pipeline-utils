yaml_file_reference_schema = {
    ## Schema #########################
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': '/schemas/YAMLFileReference',
    'title': 'YAMLFileReference',
    'description': 'Schema to validate a YAML description of a FileReference',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'Name of the FileReference',
            'type': 'string'
        },
        'description': {
            'description': 'Description of the FileReference',
            'type': 'string'
        },
        'format': {
            'description': 'Description of the FileReference',
            'type': 'string'
        },
        'version': {
            'description': 'Version of the FileReference',
            'type': 'string'
        },
        'status': {
            'description': 'Status of the upload of the FileReference',
            'type': 'string',
            'pattern': 'uploading|uploaded'
        },
        'secondary_files': {
            'description': 'Secondary files for the FileReference',
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }
    },
    'required': ['name', 'description', 'format', 'version']
}
