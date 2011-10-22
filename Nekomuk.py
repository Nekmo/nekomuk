# -*- coding: utf-8 -*-
"""
Gestor de archivos de vídeo.
"""
import os
import sys
from lxml import etree
from gettext import gettext as _
import logging
import argparse
try:
    from termcolor import cprint
except ImportError:
    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text)

try:
    # Añadir soporte para autocompletado para input
    # readline no se encuentra disponible en sistemas no-unix.
    import readline
    import glob
    def complete(text, state):
        comp_text = (glob.glob(text+'*')+[None])[state]
        if os.path.exists(comp_text) and os.path.isdir(comp_text):
            comp_text += '/'
        return comp_text
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)
except ImportError:
    pass

from nekomuk.labeldevice import LabelDevice
from nekomuk import html_build
get_device = LabelDevice()

if sys.version_info < (3,0):
    reload(sys)
    sys.setdefaultencoding('utf8')
    input = raw_input

__version__ = '0.05'

EXTS = ['mkv', 'mp4', 'avi', 'mov', 'wmv']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', dest='loglevel', action='store_const',
                        const=logging.DEBUG, default=logging.INFO,
                        help='Establecer el nivel de los logs a debug.')
    parser.add_argument('--warning', dest='loglevel', action='store_const',
                        const=logging.WARNING, default=logging.INFO,
                        help='Establecer el nivel de los logs a solo advertencias.')
    parser.add_argument('--error', dest='loglevel', action='store_const',
                        const=logging.ERROR, default=logging.INFO,
                        help='Establecer el nivel a solo errores del programa.')
    parser.add_argument('--not-update', dest='not_update', action='store_const',
                        const=True, default=False,
                        help='No actualizar el árbol de directorios..')
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format='%(levelname)-8s %(message)s')
    if not os.path.exists('config.xml'):
        cprint(_('No se ha encontrado en este directorio, "%s", ningún '\
                'proyecto de Nekomuk. ¿Desea comenzar uno?') % os.getcwd())
        if input(_('[Y/n] ')).lower().startswith(_('n')):
            cprint(_('Creación de proyecto cancelada.'))
            sys.exit(0)
        dirs = []
        while True:
            if not dirs:
                cprint(_('Porfavor, introduza la ruta al directorio con los'\
                    ' archivos de vídeo.'), 'blue')
            else:
                cprint(_('Si desea añadir un directorio más, escríbalo a '\
                        'continuación. De lo contrario, pulse Enter.'), 'blue')
            output = ''
            while not output:
                output = input('>> ')
                if not dirs and not output:
                    cprint(_('Debe introducir un directorio.'), 'red')
                elif output and not os.path.exists(output):
                    cprint(_('La ruta no existe.'), 'red')
                    output = False
                elif dirs and not output:
                    break
            if dirs and not output:
                # Se ha pulsado Enter, y por tanto no se desean añadir más
                break
            dirs.append(output)
        root = etree.Element('config')
        # Construir elemento extensions
        extensions = etree.Element('extensions')
        for ext in EXTS:
            extension = etree.Element('extension')
            extension.text = ext
            extensions.append(extension)
        root.append(extensions)
        # Se añade la versión de Nekomuk
        version = etree.Element('version')
        version.text = __version__
        root.append(version)
        # Filtros regex para nombres y directorios
        filter_dir = etree.Element('filter_dir')
        filter_dir.text = ''
        root.append(filter_dir)
        filter_filename = etree.Element('filter_filename')
        filter_filename.text = ''
        root.append(filter_filename)
        # Construir elemento dirs
        dirs_elem = etree.Element('dirs')
        for dir_ in dirs:
            device_info = get_device.get_device_by_path(dir_)
            if not device_info['label']:
                device_info['label'] = device_info['path']
            dir_elem = etree.Element('dir', device=device_info['label'])
            dir_elem.text = dir_.replace(device_info['path'], '', 1)
            dirs_elem.append(dir_elem)
        root.append(dirs_elem)
        with open('config.xml', 'w') as f:
            f.write(etree.tostring(root, pretty_print=True))
    cfg = etree.parse('config.xml')
    if not args.not_update:
        html_build(cfg)
    