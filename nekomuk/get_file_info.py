# -*- coding: utf-8 -*-
import os
import shutil
import sys
import logging
import random
import threading
import time
from gettext import gettext as _
try:
    from kaa import metadata
except ImportError:
    logging.warning(_('kaa no se encuentra instalado. No se podrán obtener'\
                      ' datos de los vídeos.'))

class GetThumb(object):
    def __init__(self, from_, to, size):
        from_ = self.parse_string(from_)
        to = self.parse_string(to)
        args = "-y -ss %i -i '%s' -f mjpeg -vframes 1 -s %ix%i -an '%s'" % \
                (300 + random.randint(0, 300), from_, size[0], size[1], to)
        os.popen(self.ffmpeg_path() % (args,))
    def ffmpeg_path(self):
        if os.name == 'nt':
            return "ffmpeg.exe %s" # WARNING Poner ruta a ffmpeg para windows
        else:
            return 'ffmpeg %s 2> /dev/null' # Comando
    
    def parse_string(self, text):
        """Parsear string para consola Bash.
        """
        for f, t in (("'", "'\"'\"'"),):
            text = text.replace(f, t)
        return text
        
from . filesize import str_size
from . get_icon import detect_dir_icon

if sys.version_info < (3,0):
    import urllib as request
    parse = request
    import urllib2
    for method in dir(urllib2):
        setattr(request, method, getattr(urllib2, method))
else:
    from urllib import parse, request
    unicode = str

THUMB_WIDTH = 120.0
MAX_THREADS = 1

def get_video_info(root, file, label, device, path):
    """Obtener información del archivo de vídeo.
    """
    orig_level = logging.getLogger().level # Recuperar el level original
    # Se sobrescribe el level para que no aparezca basura de ffmpeg
    logging.getLogger().level = logging.CRITICAL
    path_file = os.path.join(root, file)
    try:
        info = metadata.parse(path_file)
    except:
        info = {}
    project_dir = root.replace(os.path.join(device, path), '', 1)
    project_dir = os.path.join('html', 'devices',
                        parse.quote_plus(os.path.join(label, path)), project_dir)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    project_file = os.path.join(project_dir, file)
    system_file = os.path.join(root, file)
    if info and not os.path.exists(project_file + '.jpg'):
        orig_width = info['video'][0]['width']
        orig_height = info['video'][0]['height']
        if orig_height and orig_width:
            escale = orig_width / THUMB_WIDTH
            size = (THUMB_WIDTH, orig_height / escale)
            while len(threading.enumerate()) > 8:
                time.sleep(0.001)
            l = threading.Thread(target=GetThumb,
                            args=(system_file, project_file + '.jpg', size))
            l.start()
            info['thumb'] = project_file + '.jpg'
    if not info: info = {'type': 'file'}
    info['size'] = os.path.getsize(path_file)
    info['str_size'] = str_size(info['size'])
    # Se devuelve al level original.
    logging.getLogger().level = orig_level
    return info

def get_dir_info(files, path, real_root):
    """Obtener información de los archivos dentro de un directorio, y del
    propio directorio."""
    sizes_limits = {} # Tamaño medio de los archivos
    # Para los iconos, obtener la ruta relativa.
    path_parts = path.split(os.sep)
    icon = ''
    for path_part in tuple(path_parts):
        if not path_part: path_parts.remove('')
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
        icon = detect_dir_icon(os.path.join(real_root, path))
        if icon:
            dst = os.path.join('html', 'share', 'icons', parse.quote_plus(icon))
            if not os.path.exists(dst):
                shutil.copy(icon, dst)
            icon = 'share/icons/' + parse.quote(parse.quote_plus(icon))
            icon = root + icon
        else:
            icon = root + 'static/img/folder.svg' # icono por defecto
    if sizes_limits:
        first_limit = sorted(sizes_limits.items(), key=lambda x: x[1])[-1][0]
    else:
        first_limit = (-7, 7)
    mean = sum(first_limit) / 2
    return {
        'mean': mean,
        'icon': icon,
    }