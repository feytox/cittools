import os
from codecs import unicode_escape_decode, unicode_escape_encode

def getDirectory(path):
    folder_files = os.walk(path)
    res = {}
    for i in folder_files:
        res['folders'] = i[1]
        res['files'] = i[2]
        break
    return res

def fast_scandir(dirname):
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

def getProperties(file):
    res = {}
    with open(file, 'r') as f:
        strings = f.read().split('\n')
    for str1 in strings:
        str1 = str1.split('=')
        if str1 != ['']:
            res[str1[0]] = str1[1]
    return res    

def getName(file):
    return unicode_escape_decode(getProperties(file)['nbt.display.Name'])[0]

def getUniByStr(str1: str):
    return str(unicode_escape_encode(str1)[0]).replace("'\\", '').replace('\\\\', '\\').replace("'", '')[1:]

def replaceSlashes(str1: str):
    return str1.replace('\\\\', '/').replace('\\', '/')

def getCitItemTree(item: str):
    item = item.split('/cit/')[-1]
    return item.split('/')

def setProperty(file, key, value):
    new_props = getProperties(file)
    new_props[key] = value
    new_props_text = []
    for key in new_props.keys():
        new_props_text.append(f'{key}={new_props[key]}')
    with open(file, 'w') as f:
        f.write('\n'.join(new_props_text))    

def getItems() -> list[str]:
    rps = getDirectory('rp')['folders']
    cit_path = f'rp/{rps[0]}/assets/minecraft/optifine/cit'
    cit_directory = getDirectory(cit_path)
    items = []
    for file in cit_directory['files']:
        if '.properties' in file:
            items.append(cit_path + f'/{file}')
    item_folders = fast_scandir(cit_path)        
    for item_folder in item_folders:
        for file in getDirectory(item_folder)['files']:
            if '.properties' in file:
                items.append(replaceSlashes(item_folder) + f'/{file}')
    return items