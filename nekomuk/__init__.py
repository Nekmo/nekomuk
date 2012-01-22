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
import copy
from kaa import metadata
from operator import itemgetter, attrgetter
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

def cmp_lower(elements):
    return elements[0].lower()

def sorted_device(xml_elem):
    return xml_elem.attrib['device']

def new_html():
    os.mkdir('html')
    os.mkdir('html/devices')
    os.mkdir('html/s')
    os.mkdir('html/share/')
    os.mkdir('html/share/icons')
    os.mkdir('html/stats/')  

#def recursive_remove(device, tree):
    #os.path.split('html', 'devices', device, )

def html_device(name, files_by_dir, real_root, sizes):
    dirname = 'html/devices/' + parse.quote_plus(name)
    # Se borran los archivos index del device de la carpeta del proyecto
    for root, dirs, files in os.walk(dirname):
        if 'index.html' in files:
            os.remove(os.path.join(root, 'index.html'))
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
        root.append((E.div('',
            E.span(unicode(_('Nombre')), {'class': 'name'}),
            E.span(unicode(_('Tamaño')), {'class': 'size'}),
            E.span(unicode(_('Tam. predominante')), {'class': 'mean_size'}),
        {'id': 'columns_info', 'class': 'filediv'})))
        # Se añaden primero los directorios. Si hay.
        for dir in ['../'] + sorted(subtree.keys(), key=str.lower):
            if not dir: continue
            #if not os.path.join(path, dir) in files_by_dir.keys(): continue
            if '../' != dir and \
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
        for file in sorted(files, key=cmp_lower):
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
                length = file[2]['length']
                if length:
                    length = str(int(length / 60)) + _(' mins.')
                else:
                    length = '?'
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
    
    # Eliminar "directorios fantasma" (que han sido eliminados).
    for root, dirs, files in os.walk(dirname):
        root = root.replace(dirname, '')
        for dir in dirs:
            if root:
                path_dir = os.path.join(root, dir)
            else:
                path_dir = dir
            if path_dir.startswith('/'): path_dir = path_dir[1:]
            if not path_dir in files_by_dir.keys():
                shutil.rmtree(os.path.join(dirname, path_dir))

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
                pass

def make_stat(stat, device_name, real_root, files_by_dir):
    find_text = etree.XPath("//text()") # filtro XPath para buscar
    name = stat.attrib['name']
    path_device = stat.attrib['path']
    icons = {}
    icons_options = {}
    if not os.path.exists('html/stats/%s/' % name):
        os.makedirs('html/stats/%s/devices' % name)
    info = {
        'containers': {},
        'video_codecs': {},
        'dirs': 0,
        'files': 0,
        'total_size': 0,
        'total_t': 0,
        'dirs_list': [],
        }
    for icon in stat.findall('icons/icon'):
        icons[icon.attrib['name']] = copy.deepcopy(info)
        icons_options[icon.attrib['name']] = {
            'list': icon.attrib['list'],
            'legend': icon.attrib['legend'],
            }
    stats = info
    for dir, files in files_by_dir.items():
        if dir.startswith(path_device):
            dir_info = get_dir_info(files, os.path.join(real_root, dir), real_root)
            icon = dir_info['icon_name']
            add_stats_to = [stats]
            if icon in icons.keys():
                add_stats_to.append(icons[icon])
                if icons_options[icon]['list'] == '1':
                    icons[icon]['dirs_list'].append(os.path.split(dir)[-1])
                icons[icon]['about'] = icons_options[icon]
            for add_stat_to in add_stats_to:
                add_stat_to['dirs'] += 1
                add_stat_to['dirs_list'].append(os.path.split(dir)[-1])
                add_stat_to['files'] += len(files)
                for file in files:
                    if file[2].get('video', False):
                        length = file[2]['video'][0].get('length', 0)
                        container = file[2].get('type', '?')
                        video_codec = file[2]['video'][0].get('codec', '?')
                    else:
                        length = 0
                        video_codec = container = '?'
                    if not container in add_stat_to['containers'].keys():
                        add_stat_to['containers'][container] = 0
                    if not video_codec in add_stat_to['video_codecs'].keys():
                        add_stat_to['video_codecs'][video_codec] = 0
                    add_stat_to['containers'][container] += 1
                    add_stat_to['video_codecs'][video_codec] += 1
                    add_stat_to['total_t'] += length
                    add_stat_to['total_size'] += file[2]['size']
    with open('html/stats/%s/devices/%s.json' % \
                                (name, parse.quote_plus(device_name)), 'w') as f:
        f.write(json.dumps({'icons': icons, 'stats': stats}))

def devices_index():
    root = etree.Element('div')
    devices = etree.Element('ul', id='devices')
    for device in sorted(os.listdir('html/devices/')):
        if device == 'index.html': continue
        device_elem = (E.li(
            E.a(parse.unquote(device), {
                'href': 'devices/' + parse.quote_plus(device) + '/',
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
    # Índice falso en devices
    root = etree.Element('script', {'id': 'script', 'type': "text/javascript"})
    root.text = 'window.location = "../index.html"'
    with open('html/devices/index.html', 'w') as f:
        html = render_html(root, '', '', '')
        f.write(html)

def stats_index():
    stats_elem = etree.Element('ul', id='stats_index')
    stats = []
    if os.path.exists('html/stats/index.html'):
        os.remove('html/stats/index.html')
    for stat_dir in os.listdir('html/stats/'):
        elem = (E.li(E.a(stat_dir, {'href': stat_dir})))
        stats_elem.append(elem)
        stats.append(stat_dir)
    root = (E.div(
        E.h1(unicode(_('Estadísticas'))),
        stats_elem,
    {'id': 'content'}))
    with open('html/stats/index.html', 'w') as f:
        f.write(render_html(root, '', 'html/stats', '../'))
    for stat in stats:
        devices_elem = etree.Element('ul', id='devices_index')
        for dir in os.listdir('html/stats/%s/devices/' % stat):
            device = etree.Element('li', title=parse.quote_plus(dir))
            device.text = parse.unquote('.'.join(unicode(dir).split('.')[:-1]))
            devices_elem.append(device)
        root = (E.div(
            E.script("""\
            $(document).ready(function(){
                $.getScript($('#sub_root').text() + "static/js/jquery.flot.min.js");
                $.getScript($('#sub_root').text() + "static/js/jquery.flot.pie.min.js");
                $.getScript($('#sub_root').text() + 'static/js/stats.js');
            });""", {'type': 'text/javascript'}),
            E.div(
                E.div(
                    E.div(
                        E.h4('Contenedores'),
                        E.div('', {'class': 'containers'}),
                    {'class': 'graphs'}),
                    E.div(
                        E.h4(unicode('Códecs de vídeo')),
                        E.div('', {'class': 'video_codecs'}),
                    {'class': 'graphs'}),
                    E.div(
                        E.div(
                            E.span(unicode('Duración total'), {'class': 'info'}),
                            E.span('0', {'class': 'total_t', 'title': '0'}),
                        {'class': 'block_info'}),
                        E.div(
                            E.span(unicode('Tamaño total'), {'class': 'info'}),
                            E.span('0', {'class': 'total_size', 'title': '0'}),
                        {'class': 'block_info'}),
                        E.div(
                            E.span('Directorios', {'class': 'info'}),
                            E.span('0', {'class': 'sdirs', 'title': '0'}),
                        {'class': 'block_info'}),
                        E.div(
                            E.span('Archivos', {'class': 'info'}),
                            E.span('0', {'class': 'sfiles', 'title': '0'}),
                        {'class': 'block_info'}),
                        E.div(
                            E.span('Listado de directorios', {'class': 'info'}),
                            E.span('Mostrar', {'class': 'toggle', 'title': 'Ocultar'}),
                            E.ul('', {'class': 'files_list hide'}),
                        {'class': 'files_list_block'}),
                    {'class': 'blocks'}),
                    {'class': 'stats_box'}
                ),
            {'class': 'hide', 'id': 'stats_box_template'}),
            E.h1(stat),
            E.h2('Dispositivos analizados'),
            devices_elem,
            E.h2(unicode(_('Estadísticas por tipo'))),
            E.div('', {'id': 'stats_special'}),
            E.h2(unicode(_('Estadísticas totales'))),
            E.div('', {'id': 'stats_total'}),
        {'id': 'content'}))
        with open('html/stats/%s/index.html' % stat, 'w') as f:
            f.write(render_html(root, '', 'html/stats/%s' % stat, '../../',
                    css='../../static/css/stats.css'))
def legal():
    root = (E.div(
        E.script("""$(document).load(function(){
            $('#autor_div').hide();
            $('#autor_div').fadeIn();
            $('#autor_div').slideDown();
        });""", {'type': 'text/javascript'}),
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
    for dir_ in sorted(cfg.findall('dirs/dir'), key=sorted_device):
        logging.info(_('Construyendo índice de "%s"') % dir_.attrib['device'])
        if dir_.text.startswith('/'): dir_.text = dir_.text[1:]
        files, files_by_dir, real_root, sizes = search_files(dir_.attrib['device'],
                    dir_.text, exts, get_video_info,
                    filter_dir, filter_filename)
        if not os.path.exists(real_root):
            sys.stdout.write("\x08" * 80)
            sys.stdout.flush()
            logging.warning('No se pudo acceder a "%s".' % real_root)
            continue
        sys.stdout.write("\x08" * 80)
        sys.stdout.flush()
        sys.stdout.write(_('Generando archivos index del proyecto...'))
        sys.stdout.flush()
        html_device('/'.join([dir_.attrib['device'], dir_.text]),
                    files_by_dir, real_root, sizes)
        make_index('/'.join([dir_.attrib['device'], dir_.text]),
                    files, real_root)
        # Crear estadísticas para el dispositivo, si está incluido en el listado
        find_text = etree.XPath("//text()")
        device_name = '/'.join([dir_.attrib['device'], dir_.text])
        for stat in cfg.findall('stats/stat'):
            devices_in_stat = stat.findtext('devices/device')
            if not devices_in_stat or dir_.attrib['device'] in devices_in_stat:
                make_stat(stat, device_name, real_root, files_by_dir)
        sys.stdout.write(' ' * 80)
        sys.stdout.flush()
        sys.stdout.write("\x08" * 80)
        sys.stdout.flush()
        sys.stdout.write(_('Terminado\n'))
        sys.stdout.flush()
    # Se crea el índice de particiones
    stats_index()
    devices_index()
    # Añadir nota legal
    legal()
    try:
        shutil.rmtree('html/static')
    except:
        pass
    shutil.copytree(os.path.join(main_dir, 'static'), 'html/static')
    print('Terminado de indexar todos los dispositivos.')