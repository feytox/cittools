import cit_main
import base64
from os.path import exists
from id2lang import IdTranslator
import sys
import argparse

parser = argparse.ArgumentParser(description='Генератор документации к ресурспакам.')
parser.add_argument('--folder', type=str, default=None, help='название ПАПКИ ресурспака')
parser.add_argument('--name', type=str, default=None, help='название ресурспака')

translator = IdTranslator()

def progressbar(it, prefix="", size=60, out=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def getValueOrNone(dict1: dict, key) -> str:
    '''
    Получение значения словаря или None
    '''
    if key in dict1:
        return dict1[key]
    return ""    

def getMatchItemsOrNone(dict1: dict[str, str]) -> str:
    '''
    Получение соответствующих предметов предмета
    '''
    if (key := "matchItems") in dict1 or (key := "items") in dict1:
        matchItems = dict1[key].split(' ')
        matchItems = [translator.getItemNameFromLang(item.lower()) for item in matchItems if item != ""]
        return "<br>".join(matchItems)
    return ""    

def getBase64(pathToPng: str) -> str:
    '''
    Получение Base64 строки из изображения
    '''
    with open(pathToPng, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read())
    return "data:image/png;base64,"+b64_string.decode('utf-8')

def getImageOrNone(itemPath: str) -> str:
    '''
    Получение Base64 строки из пути к предмету
    '''
    if exists(imagePath := itemPath.replace(".properties", ".png")):
        return '<img src="' + getBase64(imagePath) +'" alt="">'
    return ""    

def getNameOrNone(itemPath: str) -> str:
    '''
    Получение имени предмета
    '''
    if name := cit_main.getName(itemPath):
        if ".*(" in name:
            name = name.replace("iregex:.*(", "")
            name = name.split("|")
            name = ['*' + item_name for item_name in name]
            name = "|".join(name)
        if ").*" in name:
            name = name.replace("|", "*<br>").replace(").", "")
        elif "iregex:(" in name:
            name = name.replace(")", "")
        return name.replace("ipattern:", "").replace("iregex:(", "").replace("|", "<br>").replace("iregex:", "")
    return ""    

def getLoreOrNone(dict1: dict):
    '''
    Получение подписи предмета
    '''
    lore = []
    for dict_key in dict1:
        if "nbt.display.Lore" in dict_key:
            lore.append(dict1[dict_key])
    if lore != []:
        return "<br>".join(lore)
    return ""

def getIconOrNone(rp_folder: str = None):
    '''
    Получение иконки для документации
    '''
    if icon_path := cit_main.getIcon(rp_folder):
        return f'<link rel="icon" type="image/png" sizes="16x16" href="{getBase64(icon_path)}" />'
    return ""

class Documentation:
    def __init__(self, docName: str, rp_folder: str = None, rp_name: str = None) -> None:
        self.docName = docName
        self.rp_folder = rp_folder
        if not rp_name: 
            rp_name = rp_folder
            if '/' in rp_name:
                rp_name = rp_name.split('/')[-1]
            elif '\\' in rp_name:
                rp_name = rp_name.split('\\')[-1]
        self.rp_name = rp_name

    def getAllProperties(self):
        '''
        Получение информации о всех предметах
        '''
        items = cit_main.getItems(self.rp_folder)
        self.allItems = []
        for item in items:
            item_prop = cit_main.getProperties(item)
            item_prop["path"] = item
            self.allItems.append(item_prop)

    def generateDoc(self):
        '''
        Генерация документации в файл  
        '''
        self.getAllProperties()

        with open("empty_doc.html", "r", encoding="utf-8") as f:
            empty_doc = f.read()
        docs = []
        for item in progressbar(self.allItems, "Генерация: ", 40):
            item_doc = ["<tr>"]
            # тип
            item_doc.append("<td>" + getValueOrNone(item, "type") + "</td>")
            # картинка
            item_doc.append('<td>' + getImageOrNone(item["path"]) + '</td>')
            # предметы
            item_doc.append('<td><p class="item">' + getMatchItemsOrNone(item) + "</p></td>")
            # имя
            item_doc.append("<td><p>" + getNameOrNone(item["path"]) + "</p></td>")
            # подпись (lore)
            item_doc.append('<td><p class="lore">' + getLoreOrNone(item) + "</p></td>")
            
            item_doc.append("</tr>")
            docs.append("\n".join(item_doc))
        docs = "\n".join(docs)
        empty_doc = empty_doc.replace("<!-- gendoc_rpname -->", self.rp_name).replace("<!-- gendoc_table -->", docs)
        empty_doc = empty_doc.replace("<!-- gendoc_icon -->", getIconOrNone(self.rp_folder))
        with open(self.docName + ".html", "w", encoding="utf-8") as f:
            f.write(empty_doc)

if __name__ == "__main__":
    foo = parser.parse_args()
    rp_folder = foo.folder
    rp_name = foo.name

    if not rp_folder:
        rp_folder = input('Введите название ПАПКИ ресурспака или путь к ней (ENTER, чтобы выбрать первый): ')
    if not rp_name:    
        rp_name = input("Введите отображаемое название ресурспака: (ENTER, чтобы выбрать название папки): ")
    documentation = Documentation("rp_doc", rp_folder, rp_name)
    documentation.generateDoc()
    print("Генерация документации прошла успешно!")     