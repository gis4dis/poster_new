def update_or_create(the_class, obj_def, unique_attr):
    goc_args = {
        unique_attr: obj_def[0],
        'defaults': obj_def[1],
    }
    obj, _ = the_class.objects.update_or_create(**goc_args)
    return obj


def get_or_create_objs(the_class, objs_def, unique_attr):
    objs_map = map(
        lambda obj_def: update_or_create(the_class, obj_def, unique_attr),
        objs_def
    )
    return list(objs_map)
