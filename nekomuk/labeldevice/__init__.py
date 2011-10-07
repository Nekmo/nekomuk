import sys

if sys.platform.startswith('linux'):
    from . linux import LabelDevice