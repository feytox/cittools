import os
from codecs import unicode_escape_decode, unicode_escape_encode

def getDirectory(path) -> dict:
    '''
    Получение папок и файлов из пути
    '''
    folder_files = os.walk(path)
    res = {}
    for i in folder_files:
        res['folders'] = i[1]
        res['files'] = i[2]
        break
    return res

def fast_scandir(dirname):
    '''
    Рекурсивное сканирование папки на подпапки и файлы
    '''
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

def getProperties(file) -> dict:
    '''
    Получение информации о предмете из его пути
    '''
    res = {}
    with open(file, 'r') as f:
        strings = f.read().split('\n')
    for str1 in strings:
        str1 = str1.split('=')
        if len(str1) > 1:
            res[str1[0]] = "".join(str1[1:])
    return res    

def getName(file) -> str:
    '''
    Получение имени на русском языке (вместе с iregex и т.п.)
    '''
    props = getProperties(file)
    if 'nbt.display.Name' in props:
        return unicode_escape_decode(props['nbt.display.Name'])[0]
    elif 'nbt.title' in props:
        return unicode_escape_decode(props['nbt.title'])[0]

def getUniByStr(str1: str) -> str:
    '''
    Получение Юникодовой строки из строки с русским текстом
    '''
    return str(unicode_escape_encode(str1)[0]).replace("'\\", '').replace('\\\\', '\\').replace("'", '')[1:]

def replaceSlashes(str1: str) -> str:
    '''
    Замена бэкслэшей на слэши (полезно для путей)
    '''
    return str1.replace('\\\\', '/').replace('\\', '/')

def getCitItemTree(item: str) -> list[str]:
    '''
    Получение пути к предмету от папки cit
    '''
    item = item.split('/cit/')[-1]
    return item.split('/')

def setProperty(file, key, value) -> None:
    '''
    Изменение значения настройки предмета
    '''
    new_props = getProperties(file)
    new_props[key] = value
    new_props_text = []
    for key in new_props.keys():
        new_props_text.append(f'{key}={new_props[key]}')
    with open(file, 'w') as f:
        f.write('\n'.join(new_props_text))    

def getItems(rp_name: str = None) -> list[str]:
    '''
    Получение путей всех предметов из первого ресурспака из папки rp
    '''
    rps = getDirectory('rp')['folders']
    if rp_name and rp_name in rps:
        cit_path = f'rp/{rp_name}/assets/minecraft/optifine/cit'
    else:    
        cit_path = f'rp/{rps[0]}/assets/minecraft/optifine/cit'
    cit_directory = getDirectory(cit_path)
    items = []
    if 'files' in cit_directory:
        for file in cit_directory['files']:
            if '.properties' in file:
                items.append(cit_path + f'/{file}')
    item_folders = fast_scandir(cit_path)        
    for item_folder in item_folders:
        for file in getDirectory(item_folder)['files']:
            if '.properties' in file:
                items.append(replaceSlashes(item_folder) + f'/{file}')
    return items