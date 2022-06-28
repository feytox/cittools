from telnetlib import DO
import cit_main
import base64
from os.path import exists
import json

def getValueOrNone(dict1: dict, key) -> str:
    '''
    Получение значения словаря или None
    '''
    if key in dict1:
        return dict1[key]
    return ""

def getItemNameFromLang(id: str) -> str:
    '''
    Получение имени предмета из языкового файла
    '''
    with open("ru_ru.json", "r", encoding="utf-8") as f:
        lang = f.read()
    lang_dict = json.loads(lang)
    if f'item.minecraft.{id}' in lang_dict:
        return lang_dict[f'item.minecraft.{id}']
    elif f'block.minecraft.{id}' in lang_dict:
        return lang_dict[f'block.minecraft.{id}']
    return id    

def getMatchItemsOrNone(dict1: dict) -> str:
    '''
    Получение соответствующих предметов предмета
    '''
    if "matchItems" in dict1:
        matchItems = dict1["matchItems"].split(' ')
        matchItems = [getItemNameFromLang(item) for item in matchItems]
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
        return getBase64(imagePath)
    return ""    

def getNameOrNone(itemPath: str) -> str:
    '''
    Получение имени предмета
    '''
    if name := cit_main.getName(itemPath):
        if ").*" in name:
            name = name.replace("|", "*<br>").replace(").", "")
        elif "iregex:(" in name:
            name = name.replace(")", "")
        return name.replace("ipattern:", "").replace("iregex:(", "").replace("|", "<br>")
    return ""    

class Documentation:
    def __init__(self, docName: str) -> None:
        self.docName = docName
        pass

    def getAllProperties(self):
        '''
        Получение информации о всех предметах
        '''
        items = cit_main.getItems()
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
            empty_doc = f.read().split("\n")
        docs = []
        for item in self.allItems:
            item_doc = ["<tr>"]
            # тип
            item_doc.append("<td>" + getValueOrNone(item, "type") + "</td>")
            # картинка
            item_doc.append('<td><img src="' + getImageOrNone(item["path"]) + '" alt=""></td>')
            # предметы
            item_doc.append('<td><p class="item">' + getMatchItemsOrNone(item) + "</p></td>")
            # имя
            item_doc.append("<td><p>" + getNameOrNone(item["path"]) + "</p></td>")
            # подпись (lore)
            item_doc.append('<td><p class="lore">' + getValueOrNone(item, "nbt.display.Lore") + "</p></td>")
            
            item_doc.append("</tr>")
            docs.append("\n".join(item_doc))
        docs = "\n".join(docs)
        empty_doc.insert(67, docs)
        with open(self.docName + ".html", "w", encoding="utf-8") as f:
            f.write("\n".join(empty_doc))

if __name__ == "__main__":
    documentation = Documentation("rp_doc")
    documentation.generateDoc()
    print("Генерация документации прошла успешно!")         