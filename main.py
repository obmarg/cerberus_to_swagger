from toolz import merge


def cerberus_type_to_swagger_types(cerberus_type, top_level_name):
    '''
    Takes a single cerberus type and recurses over it to build up a swagger definition.

    Each nested-level of the schema will be represented as a new swagger type.

    :param cerberus_type:   The cerberus dict definition of a type
    :param top_level_name:  The name to use for the top-level type.
    '''
    types = {}
    properties = {}
    required = []
    for key, field_data in cerberus_type.items():
        type_ = field_data['type']
        if field_data.get('required', False):
            required.append(key)
        if type_ in ('string', 'boolean'):
            properties[key] = {'type': type_}
        elif type_ == 'date':
            properties[key] = {'type': 'string', 'format': 'date'}
        elif type_ == 'list':
            if field_data['schema']['type'] in ('string', 'boolean'):
                element_data = {'type': field_data['schema']['type']}
            elif field_data['schema']['type'] == 'date':
                element_data = {'type': 'string', 'format': 'date'}
            elif field_data['schema']['type'] == 'dict':
                if key[-1] == 's':
                    item_name = snake_to_camel(key[:-1])
                else:
                    item_name = snake_to_camel(key + '_item')

                #element_data = {'type': 'object',
                #                'properties': {'$ref': '#/definitions/{}'.format(item_name)}}
                element_data = {'$ref': '#/definitions/{}'.format(item_name)}
                types = merge(
                    cerberus_type_to_swagger_types(field_data['schema']['schema'], item_name),
                    types
                )

            properties[key] = {'type': 'array', 'items': element_data}
        elif type_ == 'dict':
            item_name = snake_to_camel(key)
            properties[key] = {'$ref': '#/definitions/{}'.format(item_name)}
            types = merge(
                cerberus_type_to_swagger_types(field_data['schema'], item_name),
                types
            )

    obj = {'type': 'object', 'properties': properties}
    if required:
        obj['required'] = required

    types[top_level_name] = obj
    return types


def snake_to_camel(str_):
    return "".join(s.title() for s in str_.split('_'))
