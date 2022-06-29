import json

class IdTranslator:
    def __init__(self) -> None:
        with open("ru_ru.json", "r", encoding="utf-8") as f:
            self.lang = f.read()    

    def getItemNameFromLang(self, id: str) -> str:
        '''
        Получение имени предмета из языкового файла.
        '''
        lang_dict = json.loads(self.lang)
        if f'item.minecraft.{id}' in lang_dict:
            return lang_dict[f'item.minecraft.{id}']
        elif f'block.minecraft.{id}' in lang_dict:
            return lang_dict[f'block.minecraft.{id}']
        return id