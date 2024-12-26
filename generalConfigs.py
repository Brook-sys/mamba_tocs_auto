
import json
import os
from dotenv import load_dotenv
load_dotenv()
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
            return self.defaultvalues.get(key)
        except Exception as e:
            print('error',e)
            return default

    def set(self,key:str,value):
        self.defaultvalues[key] = value
        with open(self.pathDefaultValues, "w", encoding="utf-8") as file:
            json.dump(self.defaultvalues, file, indent=4)

class EnvValues:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.mode = os.getenv("MODE", "production")
        self.prefix_mode = "DEBUG" if self.mode == "debug" else "PROD"
        self.wpuser = os.getenv(f'WP_USER_{self.prefix_mode}')
        self.wppass = os.getenv(f'WP_PASS_{self.prefix_mode}')
        self.wpurl = os.getenv(f'WP_URL_{self.prefix_mode}')
