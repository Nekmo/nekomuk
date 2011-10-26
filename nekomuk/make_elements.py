# -*- coding: utf-8 -*-
import os
import sys
from lxml.builder import E
from lxml import etree
from gettext import gettext as _
from . filesize import str_size
from . get_file_info import get_video_info, get_dir_info
from . render_html import render_html

if sys.version_info < (3,0):
    import urllib as request
    parse = request
    import urllib2
    for method in dir(urllib2):
        setattr(request, method, getattr(urllib2, method))
else:
    from urllib import parse, request
    unicode = str

def make_elem_dir(dir, files, path, real_root, sizes):
    info = get_dir_info(files, path, real_root)
    dir_url = dir
    if dir_url[-1] != '/': dir_url += '/index.html'
    element = (
        E.div(
            E.a(E.img('', {
                    'src': info['icon'],
                    'class': 'icon',
                    'alt': '[Dir]',
                    }
                ),
                {'href': parse.quote(dir_url)}),
            E.a(unicode(dir), {'href': parse.quote(dir_url), 'class': 'name'}),
            E.span(str_size(sizes.get(os.path.join(real_root, path), 0)),
            {'class': 'size'}),
            E.span(unicode('~ %s' % str_size(info['mean'])), {'class': 'mean_size'}),
            {'class': 'filediv dir'}
        )
    )
    return element

def make_subdirs(tree, path, dirname, files_by_dir, device, real_root, sizes):
    """Hacer los índices de los directorios que sólo contienen carpetas.
    """
    if not path in files_by_dir.keys():
        if not path.split(os.sep) == 1:
            files_by_dir[path] = ()
    if not os.path.exists(os.path.join(dirname, path, 'index.html')):
        path_parts = path.split(os.sep)
        for path_part in tuple(path_parts):
            if not path_part: path_parts.remove('')
        sub_root = (len(path_parts) + 2) * '../'
        root = etree.Element('div', {'class': 'files'})
        root.append((E.div('',
            E.span(unicode(_('Nombre')), {'class': 'name'}),
            E.span(unicode(_('Tamaño')), {'class': 'size'}),
            E.span(unicode(_('Tam. predominante')), {'class': 'mean_size'}),
        {'id': 'columns_info', 'class': 'filediv'})))
        for dir in ['../'] + sorted(tree.keys(), key=str.lower):
            if not dir: continue
            if dir in files_by_dir.keys() and '../' != dir:
                subfiles = files_by_dir[os.path.join(path, dir)]
            else:
                subfiles = []
                for subfile in files_by_dir.keys():
                    subfiles.append((subfile.split('/')[0], subfile, {
                        'size': 0,
                    }))
            root.append(make_elem_dir(dir, subfiles,
                        os.path.join(path, dir), real_root, sizes))
        html = render_html(root, path, device, path)
        try:
            os.makedirs(os.path.join(dirname, path))
        except:
            pass
        with open(os.path.join(dirname, path, 'index.html'), 'w') as f:
            f.write(html)
    for subpath, subdir in tree.items():
        make_subdirs(subdir, os.path.join(path, subpath), dirname,
                     files_by_dir, device, real_root, sizes)
