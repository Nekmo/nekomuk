# -*- coding: utf-8 -*-
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
    import readline
except:
    pass

if sys.version_info < (3,0):
    reload(sys)
    sys.setdefaultencoding('utf8')
    input = raw_input
        
if not os.path.exists('config.xml'):
    cprint(_('No se ha encontrado en este directorio, "%s", ningún proyecto'\
             ' de Nekomuk. ¿Desea comenzar uno?') % os.getcwd())
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
            output = raw_input('>> ')
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
        