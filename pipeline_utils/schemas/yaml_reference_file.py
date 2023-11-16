from pipeline_utils.schemas import schema

yaml_reference_file_schema = {
    ## Schema #########################
    schema.SCHEMA: 'https://json-schema.org/draft/2020-12/schema',
    schema.ID: '/schemas/YAMLReferenceFile',
    schema.TITLE: 'YAMLReferenceFile',
    schema.DESCRIPTION: 'Schema to validate a YAML description of a ReferenceFile',
    schema.TYPE: schema.OBJECT,
    schema.PROPERTIES: {
        'name': {
            schema.DESCRIPTION: 'Name of the ReferenceFile',
            schema.TYPE: schema.STRING
        },
        'description': {
            schema.DESCRIPTION: 'Description of the ReferenceFile',
            schema.TYPE: schema.STRING
        },
        'format': {
            schema.DESCRIPTION: 'Format of the ReferenceFile',
            schema.TYPE: schema.STRING
        },
        'category': {
            schema.DESCRIPTION: 'Categories of the ReferenceFile',
            schema.TYPE: schema.ARRAY,
            schema.ITEMS: {
                schema.TYPE: schema.STRING
            }
        },
        'type': {
            schema.DESCRIPTION: 'Types of the ReferenceFile',
            schema.TYPE: schema.ARRAY,
            schema.ITEMS: {
                schema.TYPE: schema.STRING
            }
        },
        'variant_type': {
            schema.DESCRIPTION: 'Types of variants in ReferenceFile',
            schema.TYPE: schema.ARRAY,
            schema.ITEMS: {
                schema.TYPE: schema.STRING
            }
        },
        'version': {
            schema.DESCRIPTION: 'Version of the ReferenceFile',
            schema.TYPE: schema.STRING
        },
        'status': {
            schema.DESCRIPTION: 'Status of the upload of the ReferenceFile',
            schema.TYPE: schema.STRING,
            schema.PATTERN: 'uploading|uploaded'
        },
        'secondary_files': {
            schema.DESCRIPTION: 'Secondary files for the ReferenceFile',
            schema.TYPE: schema.ARRAY,
            schema.ITEMS: {
                schema.TYPE: schema.STRING
            }
        },
        'license': {
            schema.DESCRIPTION: 'License of the ReferenceFile',
            schema.TYPE: schema.STRING
        }
    },
    schema.REQUIRED: ['name', 'description', 'format', 'category', 'type', 'version']
}
