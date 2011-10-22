# -*- coding: utf-8 -*-
import os
import sys
import re
import __main__
import shutil
import glob
import json
import time
import logging
from kaa import metadata
from lxml.builder import E
from lxml import etree
from gettext import gettext as _
from . search import search_files
from . labeldevice import LabelDevice
from . filesize import str_size
from . get_file_info import get_video_info, get_dir_info
from . make_elements import make_elem_dir, make_subdirs
from . render_html import render_html

main_dir = os.path.dirname(os.path.abspath(__main__.__file__))

if sys.version_info < (3,0):
    import urllib as request
    parse = request
    import urllib2
    for method in dir(urllib2):
        setattr(request, method, getattr(urllib2, method))
else:
    from urllib import parse, request
    unicode = str

ASPECTS = {1.3333333333333333: '4:3', 1.7777777777777777: '16:9', 1: '1:1'}

def new_html():
    os.mkdir('html')
    os.mkdir('html/devices')
    os.mkdir('html/s')
    os.mkdir('html/share/')
    os.mkdir('html/share/icons')
    
def html_device(name, files_by_dir, real_root, sizes):
    dirname = 'html/devices/' + parse.quote_plus(name)
    # Se reconstruye el árbol de directorios
    tree = {}
    for path in files_by_dir.keys():
        path = path.split(os.sep)
        subtree = tree
        for dir in path:
            if not dir in subtree.keys():
                subtree[dir] = {}
            subtree = subtree[dir]
    #if os.path.exists(dirname):
        #shutil.rmtree(dirname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    for path, files in files_by_dir.items():
        if path.startswith('/'): path = path[1:]
        path_parts = path.split(os.sep)
        for path_part in tuple(path_parts):
            if not path_part: path_parts.remove('')
        sub_root = (len(path_parts) + 2) * '../'
        root = etree.Element('div', {'class': 'files'})
        try:
            os.makedirs(os.path.join(dirname, path))
        except:
            pass
        # Se busca en el árbol el directorio los directorios que hay dentro
        subtree = tree
        if path:
            for dir in path.split(os.sep):
                subtree = subtree[dir]
        else:
            subtree = subtree
        # Se añaden primero los directorios. Si hay.
        for dir in ['../'] + sorted(subtree.keys()):
            if not dir: continue
            #if not os.path.join(path, dir) in files_by_dir.keys(): continue
            if path and '../' != dir and \
                                os.path.join(path, dir) in files_by_dir.keys():
                subfiles = files_by_dir[os.path.join(path, dir)]
            else:
                subfiles = []
                for subfile in files_by_dir.keys():
                    subfiles.append((subfile.split('/')[0], subfile, {
                        'size': 0,
                    }))
            root.append(make_elem_dir(dir, subfiles, os.path.join(path, dir),
                                        real_root, sizes))
        for file in sorted(files):
            if file[2].get('video', False):
                width = file[2]['video'][0]['width']
                height = file[2]['video'][0]['height']
                if width and height:
                    aspect = width / (height * 1.0)
                    if aspect in ASPECTS.keys():
                        aspect = ASPECTS[aspect]
                    else:
                        aspect = "%0.3f" % aspect
                    width, height = str(width), str(height)
                else:
                    width = height = '???'
                container = str(file[2].get('type', '?'))
                length = str(int(file[2].get('length', 0) / 60)) + _(' mins.')
                video_codec = file[2]['video'][0]['codec']
                audio_codec = file[2]['audio'][0]['codec']
                if not video_codec:
                    video_codec = '?'
                if not audio_codec:
                    audio_codec = '?'
                fps = file[2]['video'][0].get('fps', 0)
                if fps:
                    fps = str(int(fps))
                else:
                    fps = '?'
                samplerate = file[2]['audio'][0].get('samplerate', False)
                if samplerate:
                    samplerate = '%i Khz' % (int(samplerate) / 1000,)
                else:
                    samplerate = '? Khz'
                audio_channels = str(file[2]['audio'][0].get('channels', '?'))
            else:
                width = height = container = length = aspect = fps = '???'
                video_codec = audio_codec = samplerate = audio_channels = width
            element = (
                E.div(
                    E.img('', {
                        'src': sub_root + 'static/img/video.svg',
                        'class': 'icon',
                        'alt': '[*]',
                        }
                    ),
                    E.span(unicode(file[0], errors='replace'), {
                        'class': 'name'
                    }),
                    E.span(width, {'class': 'width verbose'}),
                    E.span(height, {'class': 'height verbose'}),
                    E.span(container, {'class': 'container verbose'}),
                    E.span(length, {'class': 'length verbose'}),
                    E.span(video_codec, {'class': 'video_codec verbose'}),
                    E.span(audio_codec, {'class': 'audio_codec verbose'}),
                    E.span(aspect, {'class': 'aspect verbose'}),
                    E.span(fps, {'class': 'fps verbose'}),
                    E.span(samplerate, {'class': 'samplerate verbose'}),
                    E.span(audio_channels, {'class': 'audio_channels verbose'}),
                    E.span(file[2]['str_size'], {'class': 'size'}),
                    {'class': 'filediv file ' + file[2].get('type', 'unknown')}
                )
            )
            root.append(element)
        html = render_html(root, path, name, sub_root)
        with open(os.path.join(dirname, path, 'index.html'), 'w') as f:
            f.write(html)
    make_subdirs(tree, '', dirname, files_by_dir, name, real_root, sizes)
        
def make_index(name, files, real_root):
    dirname = 'html/s/' + parse.quote_plus(name)
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    index = {}
    for file in files:
        file = list(file)
        orig_filename = file[0]
        file[0] = file[0].decode('utf-8', errors='replace')
        file[0] = file[0].lower()
        for f, t in {'Á': 'a', 'É': 'é', 'Í': 'í', 'Ó': 'ó', 'Ú': 'ú'}.items():
            file[0] = file[0].replace(f, t)
        for word in file[0].split(' '):
            if not word[0:3] in index.keys(): index[word[0:3]] = {}
            if not word in index[word[0:3]].keys(): index[word[0:3]][word] = {}
            key = '/'.join((file[1], orig_filename))
            index[word[0:3]][word][key] = (file[0].split(' '), file[1],
                                        orig_filename, file[2]['type'])
    for term, results in index.items():
        with open(os.path.join(dirname, term + '.json'), 'w') as f:
            try:
                f.write(json.dumps(results))
            except Exception as e:
                print(term)
                print(e)

def devices_index():
    root = etree.Element('div')
    devices = etree.Element('ul', id='devices')
    for device in os.listdir('html/devices/'):
        device_elem = (E.li(
            E.a(parse.unquote(device), {
                'href': 'devices/' + parse.quote_plus(device),
                'title': device
                }),
            E.input('', {
                'type': 'checkbox',
                'checked': 'checked',
                'name': device,
                }),
        ))
        devices.append(device_elem)
    root.append(devices)
    root.append((E.span(_('Unir seleccionados'), {'class': 'merge'})))
    time_str = _('Última actualización el día %d/%m/%y, a las %H:%M:%S %Z')
    root.append(E.div(unicode(time.strftime(time_str)), {'class': 't_update'}))
    root.append(E.a(unicode(_('Nekmo Software 2011 - Licencia de uso')),
            {'class': 'license', 'href': 'legal.html'}))
    with open('html/index.html', 'w') as f:
        html = render_html(root, '', '', '')
        f.write(html)

def legal():
    root = (E.div(
        E.h1(_('Legal y licencia')),
        E.div(
            E.a('Nekmo Software 2011',
                {'href': 'http://nekmo.com', 'class': 'autor'}),
            E.a('contacto [at] nekmo.com',
                {'href': 'mailto:contacto@nekmo.com', 'class': 'mail'}),
        {'id': 'autor_div'}),
        E.div(
            E.span(unicode(_('Este proyecto, en adelante '))),
            E.em('Nekomuk Project'),
            E.span(unicode(_(' se encuentra bajo la licencia '))),
            E.a('GPLv3', {'href': 'static/licenses/GPLv3.html', 'class': 'lic'}),
            E.span(unicode(_(' salvo que se especifique lo contrario.'))),
        ),
        E.h2(unicode(_('Excepciones en la licencia'))),
        E.div(
            E.span(unicode(_('El logotipo de Nekomuk Project está basado en'\
                   ' la siguiente imagen: '))),
            E.a('Cat_silhouette.svg',
               {'href': 'http://sv.wikipedia.org/wiki/Fil:Cat_silhouette.svg'}),
            E.span(unicode(_(', el cual se encuentra bajo '))),
            E.em(unicode(_('Dominio Público'))),
        ),
        E.div(
            E.span(unicode(_('Los iconos de la colección Oxygen se encuentran'\
                    '  bajo la licencia '))),
            E.a('GPLv3', {'href': 'static/licenses/GPLv3.html', 'class': 'lic'}),
            E.span(unicode(_(' y '))),
            E.a('Creative Commons SA',
                {'href': 'static/licenses/cc_by_sa.html', 'class': 'lic'}),
        ),
        E.div(
            E.span(unicode(_('Nekmo, Nekmi, y el logotipo de la Nekmo son de '\
                            'uso personal de Nekmo, con sitio web '))),
            E.a('Nekmo.com', {'href': 'http://nekmo.com'}),
            E.span(unicode(_(' y dirección de contacto '))),
            E.a('contacto [at] nekmo.com',
                    {'href': 'mailto:contacto@nekmo.com'}),
        ),
        E.div('', {'id': 'show_license'})
    , {'id': 'legal'}))
    with open('html/legal.html', 'w') as f:
        html = render_html(root, '', '', '')
        f.write(html)

def html_build(cfg):
    if not os.path.exists('html'):
        new_html()
    exts = []
    for ext in cfg.findall('extensions/extension'):
        exts.append(ext.text)
    filter_dir = cfg.findall('filter_dir')[0].text
    filter_filename = cfg.findall('filter_filename')[0].text
    devices_files = {}
    for dir_ in cfg.findall('dirs/dir'):
        logging.info(_('Construyendo índice de "%s"') % dir_.attrib['device'])
        if dir_.text.startswith('/'): dir_.text = dir_.text[1:]
        files, files_by_dir, real_root, sizes = search_files(dir_.attrib['device'],
                    dir_.text, exts, get_video_info,
                    filter_dir, filter_filename)
        html_device('/'.join([dir_.attrib['device'], dir_.text]),
                    files_by_dir, real_root, sizes)
        make_index('/'.join([dir_.attrib['device'], dir_.text]),
                    files, real_root)
    # Se crea el índice de particiones
    devices_index()
    # Añadir nota legal
    legal()
    try:
        shutil.rmtree('html/static')
    except:
        pass
    shutil.copytree(os.path.join(main_dir, 'static'), 'html/static')