from pipeline_utils.schemas import schema

yaml_reference_genome_schema = {
    ## Schema #########################
    schema.SCHEMA: 'https://json-schema.org/draft/2020-12/schema',
    schema.ID: '/schemas/YAMLReferenceGenome',
    schema.TITLE: 'YAMLReferenceGenome',
    schema.DESCRIPTION: 'Schema to validate a YAML description of a ReferenceGenome',
    schema.TYPE: schema.OBJECT,
    schema.PROPERTIES: {
        'name': {
            schema.DESCRIPTION: 'Name of the ReferenceGenome',
            schema.TYPE: schema.STRING
        },
        'version': {
            schema.DESCRIPTION: 'Version of the ReferenceGenome',
            schema.TYPE: schema.STRING
        },
        'code': {
            schema.DESCRIPTION: 'Code for the ReferenceGenome',
            schema.TYPE: schema.STRING
        },
        'files': {
            schema.DESCRIPTION: 'Associated reference files',
            schema.TYPE: schema.ARRAY,
            schema.ITEMS: {
                schema.TYPE: schema.STRING
            }
        }
    },
    schema.REQUIRED: ['name', 'version', 'code']
}
