import copy
import datetime

def javascript_date_format(python_date_format):
    format = python_date_format.replace(r'Y', 'yyyy')
    format = format.replace(r'm', 'mm')
    format = format.replace(r'd', 'dd')
    if not format:
        format = 'yyyy-mm-dd'
    return format

def duplicate(obj, changes=None):
    """ Duplicates any object including m2m fields
    changes: any changes that should occur, example
    changes = (('fullname','name (copy)'), ('do not copy me', ''))"""
    if not obj.pk:
        raise ValueError('Instance must be saved before it can be cloned.')
    duplicate = copy.copy(obj)
    duplicate.pk = None
    for change in changes:
        duplicate.__setattr__(change[0], change[1])
    duplicate.save()
    # trick to copy ManyToMany relations.
    for field in obj._meta.many_to_many:
        source = getattr(obj, field.attname)
        destination = getattr(duplicate, field.attname)
        for item in source.all():
            try: # m2m, through fields will fail.
                destination.add(item)
            except: pass
    return duplicate


DATE = 1
NUMBER = 2

def sort_helper(x, sort_key, sort_type):
    """ Sadly python 3 makes it very hard to sort mixed types
        We can work around this by forcing the types
    """
    result = x[sort_key]
    if result is None:
        if sort_type == DATE:
            result = datetime.date(datetime.MINYEAR, 1, 1)
        elif sort_type == NUMBER:
            result = 0
        else:  # Last try - make it a string
            result = ''
    return result


def sort_data(data_list, display_field):
    position = display_field.position
    is_reverse = display_field.sort_reverse
    # Try to inspect sample data to determine type
    sample_data = data_list[0][position]
    if sample_data is None:
        sample_data = data_list[-1][position]
    sort_type = None
    if isinstance(sample_data, (datetime.date, datetime.datetime)):
        sort_type = DATE
    elif isinstance(sample_data, (int, float, complex)):
        sort_type = NUMBER
    return sorted(
        data_list,
        key=lambda x: sort_helper(x, position, sort_type),
        reverse=is_reverse
    )
