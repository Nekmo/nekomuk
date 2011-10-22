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
    last_filename_length = 0
    for root, dirs, files in os.walk(root_path):
        if filter_dir and not re.match(filter_dir, os.path.split(root)[1]):
            continue
        total_size = 0
        root_ = root.replace(root_path, '', 1)
        for file in files:
            if file == 'index.html':
                os.remove(os.path.join(root, file))
                continue
            if not file.split('.')[-1] in exts:
                continue
            if filter_filename and not len(re.match(file, filter_filename)):
                continue
            if last_t != int(time.time()):
                sys.stdout.write("\x08" * last_filename_length)
                last_filename_length = len(os.path.join(root, file))
                sys.stdout.flush()
                sys.stdout.write(os.path.join(root, file))
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
    print('')
    return sorted(files_list), files_by_dir, root_path, size_by_dir