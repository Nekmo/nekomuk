# -*- coding: utf-8 -*-
import os
import glob
import re
import shutil

def get_kde_path_icons():
    """Obtener el path donde se encuentran los iconos del tema en uso.
    - Ejemplo de salida: /usr/share/icons/oxygen/32x32/places/
    Esto necesario porque en los .directory con los metadata del directorio
    (entre los que se encuentra el icono), a veces no se encuentra la ruta
    al icono, sino el nombre del mismo.
    """
    # Se busca el directorio de configuración de KDE, de lo contrario, falla
    if not glob.glob1(os.environ['HOME'], '.kde*'):
        return False
    kdeglobals = ''
    # Comprobar si el nombre del mismo es .kde4 o .kde. Depende la distro.
    for dircfg in ['.kde4', '.kde']:
        if os.path.exists(os.path.join(os.environ['HOME'], dircfg)):
            kdeglobals = os.path.join(os.environ['HOME'], dircfg,
                                        'share', 'config', 'kdeglobals')
            break
    if not kdeglobals:
        return False
    # Se abre el archivo de configuración "kdeglobals" para buscar el nombre
    # del tema de iconos
    with open(kdeglobals) as f:
        theme = re.findall('Theme=(.+)', f.read(), re.MULTILINE)
    if not theme:
        return False
    theme_dir = False
    # El tema de iconos puede encontrarse o bien en el directorio del usuario,
    # o en /usr/share/icons. tiene preferencia el primero.
    for dir in [os.path.join(os.environ['HOME'], dircfg, 'share', 'icons'),
            '/usr/share/icons']:
        if os.path.exists(os.path.join(dir, theme[0])):
            theme_dir = os.path.join(dir, theme[0])
            # Existe el siguiente problema: Algunos temas de iconos pueden
            # tener como estructura <tamaño>/<tipo>, y en otros como
            # <tipo>/<tamaño>. Además, el tamaño no siempre es igual, a veces
            # es 32x32, y en otras 32.
            if glob.glob1(theme_dir, '32*'):
                size_dir = glob.glob1(theme_dir, '32*')
                theme_dir = os.path.join(theme_dir, size_dir[0], 'places')
                break
            elif glob.glob1(theme_dir, 'places'):
                size_dir = glob.glob1(os.path.join(theme_dir, 'places'), '32*')
                theme_dir = os.path.join(theme_dir, 'places', size_dir[0])
                break
    if theme_dir and os.path.exists(theme_dir):
        return theme_dir
    else:
        return False

# Iconos para KDE
kde_icons = get_kde_path_icons()

def detect_dir_icon(root):
    """Detectar si el directorio tiene un icono, y si es afirmativo, devolver
    la ruta del mismo.
    """
    if not os.path.exists(root):
        return False
    # KDE
    if '.directory' in os.listdir(root):
        # .directory es un archivo de meta-datos que se encuentra dentro del
        # directorio con información sobre el mismo, uno de los datos posibles
        # es el icono.
        data = open(os.path.join(root, '.directory')).read()
        icon = re.findall('Icon=(.+)', data, re.MULTILINE)
        if not icon:
            return False
        icon = icon[0]
        if not icon.startswith('/') and kde_icons:
            # El icono no es una ruta al icono, sino el nombre del mismo, y se
            # necesita obtener del directorio del tema de iconos del sistema.
            icon = glob.glob1(kde_icons, icon + '*')
            if icon:
                return os.path.join(kde_icons, icon[0])
            else:
                return False
        if not icon.startswith('/') and not kde_icons:
            # Es como el caso anterior un nombre del icono, pero no se posee
            # el directorio de iconos, por lo que el proceso fallará
            return False
        else:
            # Es una ruta al icono, se devuelve
            return icon
    return False