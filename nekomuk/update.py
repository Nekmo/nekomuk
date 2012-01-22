# -*- coding: utf-8 -*-
import os
import logging
import __main__
from lxml import etree
main_dir = os.path.dirname(os.path.abspath(__main__.__file__))
cfg = etree.parse('config.xml').getroot()

if not cfg.findall('stats'):
    logging.info('Actualización 0.0.6: Soporte de estadísticas.')
    stats_elem = etree.Element('stats')
    cfg.append(stats_elem)

cfg.find('version').text = __main__.__version__

with open('config.xml', 'w') as f:
    f.write(etree.tostring(cfg, pretty_print=True))