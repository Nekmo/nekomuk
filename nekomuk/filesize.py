# -*- coding: utf-8 -*-

sizes = {'b': 1, 'B': 8, 'KiB': 1024, 'MiB': 1048576.0, 'GiB': 1073741824.0}

def get_float(num, size):
    if round(num / size, 1) == num // size:
        num = int(num // size)
    else:
        num = round(num / size, 1)
    return num

def str_size(num):
    """Pasar el tamaño en bytes, a un string legible 'para humanos'"""
    for size in sizes.keys():
        if num / 1024 >  sizes[size]:
            pass
        else:
            num = get_float(num, sizes[size])
            return '%s %s' % (num, size)
    # No se encuentra dentro de los rangos, se usa el último visto
    num = get_float(num, sizes[size])
    return '%s %s' % (num, size)