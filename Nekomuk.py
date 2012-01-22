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

__version__ = '0.06'

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
                        help='No actualizar el árbol de directorios.')
    parser.add_argument('--add-stat', dest='add_stat', action='store_const',
                        const=True, default=False,
                        help='Añadir un nuevo proyecto de estadística.')
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
                    ' archivos de vídeo.'), 'green')
            else:
                cprint(_('Si desea añadir un directorio más, escríbalo a '\
                        'continuación. De lo contrario, pulse Enter.'), 'green')
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
            if output and not output.endswith('/'):
                output += '/'
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
        # Se añade el grupo de estadísticas
        root.append(etree.Element('stats'))
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
    cfg = etree.parse('config.xml').getroot()
    if cfg.find('version').text != __version__:
        cprint(_('La versión de Nekomuk difiere con la de la configuración '\
                'del proyecto. ¿Desea actualizar ahora?'), 'yellow')
        cprint(_('Versión de Nekomuk %s. Versión del proyecto: %s') % \
                (__version__, cfg.find('version').text), 'yellow')
        if (input(_('[Y/n]')))[0].lower() == _('n'):
            sys.exit(0)
        else:
            from nekomuk import update
    if args.add_stat:
        name = ''
        while not name:
            cprint(_('Introduzca un nombre para el proyecto de estadísticas.'),
                    'green')
            name = input('>> ')
        devices = []
        cprint(_('Introduza los dispositivos en los que se buscará. Deje en'\
                ' blanco para añadir todos.'),
                'green')
        device = input('>> ')
        if device:
            devices.append(device)
            while device:
                cprint(_('Si lo desea, añada otro. Enter para cancelar.'),
                        'green')
                if device: devices.append(device)
        cprint(_('En caso de querer buscar dentro de una ruta específica '\
                'dentro de los dispositivos, introdúzcala o pulse enter.'),
                'green')
        path_device = input('>> ')
        icons = {}
        while True:
            cprint(_('Si lo desea, puede añadir estadísticas por icono de '\
                    'carpeta. Introduza el nombre de archivo del icono en '\
                    'share/icons/ para continuar. Deje en blanco para cancelar'),
                    'green')
            icon = input('>> ')
            if not icon: break
            icons[icon] = {}
            cprint(_('Introduza la leyenda para el icono (serie vista, serie '\
                    'pendiente...).'), 'green')
            icons[icon]['legend'] = input('>> ')
            cprint(_('¿Desea listar los directorios con este icono de carpeta?'),
                    'green')
            if (input(_('[Y/n]')))[0].lower() == _('n'):
                icons[icon]['list'] = '0'
            else:
                icons[icon]['list'] = '1'
        stat_elem = etree.Element('stat', name=name, path=path_device)
        devices_elem = etree.Element('devices')
        for device in devices:
            device_elem = etree.Elem('device')
            device_elem.text = device
            devices_elem.append(device_elem)
        stat_elem.append(devices_elem)
        icons_elem = etree.Element('icons')
        for icon_name, icon_data in icons.items():
            icon_elem = etree.Element('icon', name=icon_name,
                        legend=icon_data['legend'], list=icon_data['list'])
            icons_elem.append(icon_elem)
        stat_elem.append(icons_elem)
        root = etree.parse('config.xml')
        root.findall('stats')[0].append(stat_elem)
        with open('config.xml', 'w') as f:
            f.write(etree.tostring(root, pretty_print=True))
        cfg = etree.parse('config.xml')
    elif not args.not_update:
        html_build(cfg)
