import os
import re
import time
import sys
from . labeldevice import LabelDevice
get_device = LabelDevice()

def search_files(label, path, exts, callback, filter_dir, filter_filename):
    files_list = []
    files_by_dir = {}
    size_by_dir = {}
    device = get_device.get_device_by_label(label)
    if not device:
        device = label
    else:
        device = device['path']
    root_path = os.path.join(device, path)
    last_t = int(time.time())
    ignore_dirs = []
    for root, dirs, files in os.walk(root_path):
        root_ = root.replace(root_path, '', 1)
        if (root_ and filter_dir and \
                            not re.match(filter_dir, os.path.split(root_)[1])):
            ignore_dirs.append(root_)
            continue
        for ignore_dir in ignore_dirs:
            if root_.startswith(ignore_dir): continue
        total_size = 0
        for file in files:
            if not file.split('.')[-1] in exts:
                continue
            if filter_filename and not re.match(filter_filename, file):
                continue
            if last_t != int(time.time()):
                file_ = file
                if len(file_) > 80: file_ = '...' + file_[:-78]
                sys.stdout.write("\x08" * 80)
                sys.stdout.flush()
                reset_length = 80 - len(file_)
                if reset_length < 0: reset_length = 0
                sys.stdout.write(file_ + (' ' * reset_length))
                sys.stdout.flush()
                last_t = int(time.time())
            total_size += os.path.getsize(os.path.join(root, file))
            callback_data = callback(root, file, label, device, path)
            files_list.append((file, root_, callback_data))
            if not root_ in files_by_dir.keys():
                files_by_dir[root_] = []
            files_by_dir[root_].append((file, root_, callback_data))
        size_by_dir[root] = total_size
        for dir in dirs:
            files_list.append((dir, root_, {'size': 0, 'type': 'dir'}))
    sys.stdout.write("\x08" * 80)
    sys.stdout.flush()
    sys.stdout.write(' ' * 80)
    sys.stdout.flush()
    return sorted(files_list), files_by_dir, root_path, size_by_dir