import os
from . labeldevice import LabelDevice
get_device = LabelDevice()

def search_files(label, path, exts, callback):
    files_list = []
    files_by_dir = {}
    device = get_device.get_device_by_label(label)
    if not device:
        device = label
    else:
        device = device['path']
    if path.startswith('/'): path = path[1:]
    root_path = os.path.join(device, path)
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if not file.split('.')[-1] in exts:
                continue
            root_ = root.replace(root_path, '', 1)
            callback_data = callback(root, file)
            files_list.append((file, root_, callback_data))
            if not root_ in files_by_dir.keys():
                files_by_dir[root_] = []
            files_by_dir[root_].append((file, root_, callback_data))
    return sorted(files_list), files_by_dir