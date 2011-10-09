# -*- coding: utf-8 -*-
import os
import sys
import re
import __main__
import shutil
from kaa import metadata
from lxml.builder import E
from lxml import etree
from gettext import gettext as _
from . search import search_files
from . labeldevice import LabelDevice

main_dir = os.path.dirname(os.path.abspath(__main__.__file__))
sizes = {'b': 1, 'B': 8, 'KiB': 1024, 'MiB': 1048576.0, 'GiB': 1073741824.0}

if sys.version_info < (3,0):
    import urllib as request
    parse = request
    import urllib2
    for method in dir(urllib2):
        setattr(request, method, getattr(urllib2, method))
else:
    from urllib import parse, request
    unicode = str

renders = {}
renders['base'] = open(os.path.join(main_dir, 'templates/base.html')).read()

def get_kde_path_icons():
    if not glob.glob1(os.environ['HOME'], '.kde*'):
        return False
    kdeglobals = ''
    for dircfg in ['.kde4', '.kde']:
        if os.path.exists(os.path.join(os.environ['HOME'], dircfg):
            kdeglobals = os.path.join(os.environ['HOME'], dircfg,
                                        'share', 'config', 'kdeglobals')
            break
    if not kdeglobals:
        return False
    with open(kdeglobals) as f:
        theme = re.findall('Theme=(.+)', f.read(), re.MULTILINE)
    if not theme:
        return False
    theme_dir = False
    for dir in [os.path.join(os.environ['HOME'], dircfg, 'share', icons),
            '/usr/share/icons']:
        if os.path.exists(os.path.join(dir, theme)):
            theme_dir = os.path.join(dir, theme)
            if glob.glob1(theme_dir, '32*'):
                size_dir = glob.glob1(theme_dir, '32*')
                return os.path.join(theme_dir, size_dir, 'places')
            elif glob.glob1(theme_dir, 'places'):
                size_dir = glob.glob1(os.path.join(theme_dir, 'places'), '32*')
                return os.path.join(theme_dir, 'places', size_dir)
    
# Iconos para KDE
kde_icons = get_kde_path_icons()

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

def render_html(content, path, device, title='', top='', render='base'):
    if not title:
        title = '[%s]%s' % (device, path)
    title_elem = etree.Element('title')
    title_elem.text = unicode(_('%s - Nekomuk') % title, errors='replace')
    path_parts = os.path.split(path)
    if not path_parts[-1]:
        path_parts = path_parts[:-1]
    root = (len(path_parts) + 1) * '../'
    if not top:
        top = (
            E.div(
                E.div(
                    E.input({
                        'type': 'text',
                        'value': unicode(_('¿Qué desea buscar hoy?')),
                        }
                    ),
                    {'id': 'search'},
                ),
                E.div(
                    E.Span({
                        'class': 'icons',
                        'title': unicode(_('Modo de Vista de iconos')),
                        }
                    ),
                    E.Span({
                            'title': _('Modo de vista detallada'),
                            'class': 'details'
                        }
                    ),
                    {'id': 'view'},
                ),
                {'id': "subtop"}
            )
        )
        
    return renders[render] % {
        'content': etree.tostring(content),
        'title': etree.tostring(title_elem),
        'js': '',
        'css': '',
        'top': etree.tostring(top),
        'root': root,
    }

def get_video_info(root, file):
    path_file = os.path.join(root, file)
    try:
        1 / 0
        info = metadata.parse(path_file)
    except:
        info = {}
    if not info: info = {}
    info['size'] = os.path.getsize(path_file)
    info['str_size'] = str_size(info['size'])
    return info

def detect_dir_icon(root):
    default = 'default.png'
    # KDE
    if '.directory' in os.listdir(root):
        data = open(os.path.join(root, '.directory')).read()
        icon = re.findall('Icon=(.+)', data, re.MULTILINE)

def get_dir_info(files, path, real_root):
    """Obtener información de los archivos dentro de un directorio, y del
    propio directorio."""
    sizes_limits = {} # Tamaño medio de los archivos
    # Para los iconos, obtener la ruta relativa.
    path_parts = os.path.split(path)
    if not path_parts[-1]:
        path_parts = path_parts[:-1]
    root = (len(path_parts) + 1) * '../'
    for file in files:
        # Tamaño medio de los archivos
        in_limits = False
        for limit in sizes_limits.keys():
            if limit[0] < file[2]['size'] and file[2]['size'] < limit[1]:
                in_limits = True
                sizes_limits[limit] += 1
                break
        if not in_limits:
            margin = 1024 * 1024 * 7
            key_limits = (file[2]['size'] - margin, file[2]['size'] + margin)
            sizes_limits[key_limits] = 1
        # Detectar icono del directorio
        detect_dir_icon(os.path.join(real_root, path))
    if sizes_limits:
        first_limit = sorted(sizes_limits.items(), key=lambda x: x[1])[-1][0]
    else:
        first_limit = (-7, 7)
    mean = sum(first_limit) / 2
    return {
        'mean': mean,
    }
    
def new_html():
    os.mkdir('html')
    os.mkdir('html/devices')
    os.mkdir('html/s')

def make_elem_dir(dir, files, path, real_root):
    info = get_dir_info(files, path, real_root)
    element = (
        E.div(
            E.a(dir, {'href': parse.quote(dir), 'class': 'name'}),
            E.span(unicode('~ %s' % str_size(info['mean'])), {'class': 'mean_size'}),
            {'class': 'filediv dir'}
        )
    )
    return element

def make_subdirs(tree, path, dirname, files_by_dir, device, real_root):
    """Hacer los índices de los directorios que sólo contienen carpetas.
    """
    if not os.path.exists(os.path.join(dirname, path, 'index.html')):
        root = etree.Element('div', {'class': 'files'})
        for dir in tree.keys():
            if path:
                subfiles = files_by_dir[os.path.join(path, dir)]
            else:
                subfiles = []
                for subfile in files_by_dir.keys():
                    subfiles.append((subfile.split('/')[0], subfile, {
                        'size': 0,
                    }))
            root.append(make_elem_dir(dir, subfiles,
                        os.path.join(path, dir), real_root))
        html = render_html(root, path, device)
        try:
            os.makedirs(os.path.join(dirname, path))
        except:
            pass
        with open(os.path.join(dirname, path, 'index.html'), 'w') as f:
            f.write(html)
    for subpath, subdir in tree.items():
        make_subdirs(subdir, os.path.join(path, subpath), dirname,
                     files_by_dir, device, real_root)
    
def html_device(name, files_by_dir, real_root):
    dirname = 'html/devices/' + parse.quote_plus(name)
    # Se reconstruye el árbol de directorios
    tree = {}
    for path in files_by_dir.keys():
        path = os.path.split(path)
        subtree = tree
        for dir in path:
            if not dir in subtree.keys():
                subtree[dir] = {}
            subtree = subtree[dir]
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    for path, files in files_by_dir.items():
        if path.startswith('/'): path = path[1:]
        root = etree.Element('div', {'class': 'files'})
        # Se busca en el árbol el directorio los directorios que hay dentro
        subtree = tree
        if path:
            for dir in os.path.split(path):
                subtree = subtree[dir]
        else:
            subtree = subtree['']
        # Se añaden primero los directorios. Si hay.
        for dir in sorted(subtree.keys()):
            if not dir: continue
            if path:
                subfiles = files_by_dir[os.path.join(path, dir)]
            else:
                subfiles = []
                for subfile in files_by_dir.keys():
                    subfiles.append((subfile.split('/')[0], subfile, {
                        'size': 0,
                    }))
            root.append(make_elem_dir(dir, subfiles, os.path.join(path, dir),
                                        real_root))
        for file in sorted(files):
            element = (
                E.div(
                    E.span(unicode(file[0], errors='replace'), {
                        'class': 'name'
                    }),
                    E.span(file[2]['str_size'], {'class': 'size'}),
                    {'class': 'filediv file ' + file[2].get('type', 'unknown')}
                )
            )
            root.append(element)
        html = render_html(root, path, name)
        try:
            os.makedirs(os.path.join(dirname, path))
        except:
            pass
        with open(os.path.join(dirname, path, 'index.html'), 'w') as f:
            f.write(html)
    make_subdirs(tree, '', dirname, files_by_dir, name, real_root)
        

def html_build(cfg):
    if not os.path.exists('html'):
        new_html()
    exts = []
    for ext in cfg.findall('extensions/extension'):
        exts.append(ext.text)
    devices_files = {}
    for dir_ in cfg.findall('dirs/dir'):
        files, files_by_dir, real_root = search_files(dir_.attrib['device'],
                                            dir_.text, exts, get_video_info)
        html_device(dir_.attrib['device'], files_by_dir, real_root)
    