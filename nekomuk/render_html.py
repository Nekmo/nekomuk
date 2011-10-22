# -*- coding: utf-8 -*-
import os
import sys
import __main__
from lxml.builder import E
from lxml import etree
from gettext import gettext as _

if sys.version_info < (3,0):
    import urllib as request
    parse = request
    import urllib2
    for method in dir(urllib2):
        setattr(request, method, getattr(urllib2, method))
else:
    from urllib import parse, request
    unicode = str

main_dir = os.path.dirname(os.path.abspath(__main__.__file__))
renders = {}
renders['base'] = open(os.path.join(main_dir, 'templates/base.html')).read()
    
def render_html(content, path, device, sub_root, title='', top='', render='base',
                search_mode=1):
    if not title:
        title = '[%s]%s' % (device, path)
    title_elem = etree.Element('title', id='title')
    title_elem.text = unicode(_('%s - Nekomuk') % title, errors='replace')
    path_parts = path.split(os.sep)
    for path_part in tuple(path_parts):
        if not path_part: path_parts.remove('')
    if device:
        root = (len(path_parts) + 2) * '../'
    else:
        root = ''
    s1 = s2 = s3 = 'title'
    if search_mode == 1:
        s1 = 'checked'
    elif search_mode == 2:
        s2 = 'checked'
    else:
        s3 = 'checked'
    if not top:
        top = (
            E.div(
                E.div(
                    E.input('', {
                        'type': 'text',
                        'title': unicode(_('¿Qué desea buscar hoy?')),
                        }
                    ),
                    {'id': 'search'},
                ),
                E.div(
                    E.span(_('Avanzado'), {'class': 'show_advance'}),
                    E.div(
                        E.div(
                            E.input('', {'type': 'radio', 'name': 'advance',
                                    'id': 'search_1', s1: s1, 'value': '1'}),
                            E.label(unicode(_('Sólo aquí')), {'for': 'search_1'}),
                        ),
                        E.div(
                            E.input('', {'type': 'radio', 'name': 'advance',
                                    'id': 'search_2', s2: s2, 'value': '2'}),
                            E.label(unicode(_('Dispositivo')), {'for': 'search_2'}),
                        ),
                        E.div(
                            E.input('', {'type': 'radio', 'name': 'advance',
                                        'id': 'search_3', s3: s3, 'value': '3'}),
                            E.label(unicode(_('Todos los dispositivos')),
                                    {'for': 'search_3'}),
                        ),
                    {'class': 'advance'}),
                ),
                E.div(
                    E.Span('', {
                        'class': 'icons',
                        'title': unicode(_('Modo de Vista de iconos')),
                        }
                    ),
                    E.Span('', {
                            'title': _('Modo de vista detallada'),
                            'class': 'details'
                        }
                    ),
                    {'id': 'view'},
                ),
                {'id': "subtop"}
            )
        )
    locals = (
        E.div('',
            E.div('',
                E.span(_('Res.'), {'class': 'resolution_text'}),
                E.span(unicode(_('Tamaño')), {'class': 'size_text'}),
                E.span(unicode(_('códec video')), {'class': 'video_codec_text'}),
                E.span(unicode(_('códec audio')), {'class': 'audio_codec_text'}),
                E.span(_('Rel. aspecto'), {'class': 'aspect_text'}),
                E.span(_('FPS.'), {'class': 'fps_text'}),
                E.span(_('Durac.'), {'class': 'length_text'}),
                E.span(_('Contenedor'), {'class': 'container_text'}),
                E.span(_('Frec. audio'), {'class': 'samplerate_text'}),
                E.span(_('Canales audio'), {'class': 'audio_channels_text'}),
            {'title': '#panel'}),
        {'id': 'locals'})
    )
            
            
    return renders[render] % {
        'content': etree.tostring(content),
        'title': etree.tostring(title_elem),
        'js': '',
        'css': '',
        'locals': etree.tostring(locals),
        'sub_root': etree.tostring((E.div(root, {'id': 'sub_root'}))),
        'device': etree.tostring((E.div(parse.quote_plus(device),
                                {'id': 'device'}))),
        'top': etree.tostring(top),
        'root': root,
    }
    