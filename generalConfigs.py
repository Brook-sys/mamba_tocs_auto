
import json
class DefaultValues:
    def __init__(self, pathDefaultValues='defaultvalues.json'):
        self.pathDefaultValues  = pathDefaultValues
        self.defaultvalues      = self.load_default_values(self.pathDefaultValues)
        
    def load_default_values(self,file_path):
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar o arquivo JSON: {e}")
            return None

    def get(self,key:str,default=None):
        try:
            return self.defaultvalues.get[key]
        except Exception as e:
            return default

    def set(self,key:str,value):
        self.defaultvalues[key] = value
        with open(self.pathDefaultValues, "w", encoding="utf-8") as file:
            json.dump(self.defaultvalues, file, indent=4)