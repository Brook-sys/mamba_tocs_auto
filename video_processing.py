import json
import re
import unicodedata
import time
from llama_index.llms.groq import Groq
import sys
import os

inColab = "google.colab" in sys.modules
userdata= None
if inColab:
  userdata = __import__('google.colab.userdata', fromlist=['userdata'])
else:
  from dotenv import load_dotenv
  load_dotenv()
groq_api_key = userdata.get("GROQ_API_KEY") if userdata else os.getenv("GROQ_API_KEY")
mode = userdata.get('MODE') if userdata else os.getenv('MODE', 'production')

class xvideosVideo:
  def __init__(self,title='',thumb='',duration=0,embed='',video_url='',trailer_url='',xv_url='',tags=[],xv_origin=None):
    self.title = title if title else xv_origin.title
    
    self.slug = self.tranform_str(self.title)
    self.video_url = video_url
    self.thumbnail_url = thumb if thumb else xv_origin.thumbnail_url
    self.trailer_url = trailer_url if trailer_url else self.convert_thumb_to_vid(self.thumbnail_url)
    self.length = self.time_xv_to_sec(duration if duration else xv_origin.length)
    self.url = xv_url if xv_url else xv_origin.url
    self.id = self.extract_id_from_url(self.url)
    self.tags = tags if tags else xv_origin.tags
    self.embed_url = f'https://videoscdn.online/{self.id}'
    embed_xv_cdn = f'<iframe src="{self.embed_url}" frameborder=0 width=510 height=400 scrolling=no allowfullscreen=allowfullscreen></iframe>'
    self.embed_iframe = embed if embed else embed_xv_cdn
    
    
    self.video = Video(
      title = self.title,
      embed_url = self.embed_url,
      embed_iframe=self.embed_iframe,
      slug = self.slug,
      video_url = self.video_url,
      thumbnail_url = self.thumbnail_url,
      trailer_url = self.trailer_url,
      length = self.length,
      url = self.url,
      id = self.id,
      tags = self.tags
    )
    
  def tranform_str(self,original:str) -> str:
      try:
        return re.sub(r'-+', '-', re.sub(r'\s+', '-', re.sub(r'[^a-z0-9\s-]', '-', unicodedata.normalize('NFKD', original.lower()).encode('ASCII', 'ignore').decode('utf-8')))).strip('-')
      except:
        return 'porn-mature-sex'

  def time_xv_to_sec(self,time_str)->int:
      try:
        hours = int(re.search(r'(\d+)\s*h', time_str).group(1)) * 3600 if re.search(r'(\d+)\s*h', time_str) else 0
        minutes = int(re.search(r'(\d+)\s*min', time_str).group(1)) * 60 if re.search(r'(\d+)\s*min', time_str) else 0
        seconds = int(re.search(r'(\d+)\s*sec', time_str).group(1)) if re.search(r'(\d+)\s*sec', time_str) else 0
        return hours + minutes + seconds
      except:
        return 120

  def convert_thumb_to_vid(self,url)-> str:
    base_url = re.sub(r'/thumbs(169)?(xnxx)?(l*|poster)/', '/videopreview/', url[:url.rfind("/")])
    suffix = re.search(r'-(\d+)', base_url)
    base_url = re.sub(r'-(\d+)', '', base_url) if suffix else base_url
    return f"{base_url}_169{suffix.group(0) if suffix else ''}.mp4"

  def extract_id_from_url(self,url)-> str:
    pattern = r'/video\.([a-zA-Z0-9_]+)\/'
    match = re.search(pattern, url)
    return match.group(1) if match else ''
  
class Video:
  
  def __init__(self, title='',embed_url='',embed_iframe='',slug='',video_url='',thumbnail_url='',trailer_url='',length=120,url='',id='',tags=[]) -> None:
    self.title = title
    self.embed_url = embed_url
    self.slug = slug
    self.video_url = video_url
    self.thumbnail_url = thumbnail_url
    self.trailer_url = trailer_url
    self.length = length
    self.url = url
    self.id = id
    self.tags = tags
    self.embed_iframe = embed_iframe
    
    self.llm = Groq(model="llama-3.1-70b-versatile", api_key=groq_api_key)
    self.desc = ''
    self.title = self.title
    self.meta_desc = ''
    self.image_alt = ''
    self.keywords = ''
    #self.getIaTexts() if not mode == 'debug' else None
    
  def getIaTexts(self):
    
    with open("localprompts.json", "r") as f:
        prompts = json.load(f)
    try:
        self.desc = self.exec_prompt(prompts["descricao"].format(titulo=self.title, tags=str(self.tags)))
        self.title = self.exec_prompt(prompts["titulo"].format(titulo=self.title, tags=str(self.tags)))
        self.meta_desc = self.exec_prompt(prompts["meta_descricao"].format(titulo=self.title, descricao=self.desc))
        self.image_alt = self.exec_prompt(prompts["imagem_alt"].format(titulo=self.title, tags=str(self.tags)))
        self.keywords = self.exec_prompt(prompts["palavras_chave"].format(titulo=self.title, tags=str(self.tags)))
        #print(f'\n\n------\n\n{self.title}\n\n{self.desc}\n\n{self.meta_desc}\n\n{self.image_alt}\n\n{self.keywords}\n\n------\n\n')
    except Exception as e:
        print(f"Erro na chamada da API: {e}")
        time.sleep(60) # Pausa de 1 minuto em caso de erro
        return self.getIaTexts() 

  def exec_prompt(self,prompt):
    time.sleep(2)
    return str(self.llm.complete(prompt)).replace('"','').replace("'","")
class SearchConfig:
  def __init__(self,firevalues):
    self.pathDefaultValues  = 'defaultvalues.json'
    self.defaultvalues      = self.load_default_values(self.pathDefaultValues)
    self.source             = firevalues or self.defaultvalues
    self.source             = self.defaultvalues if mode == 'debug' else self.source
    self.terms              = self.source.get('termos')
    self.min_daily          = self.source.get('minimoDiario')
    self.search_qty         = self.source.get('qtyPorTermo')
    self.max_attempts       = self.source.get('maxTentativas')
  def load_default_values(self,file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        return None

class VideoSearcher:
  def __init__(self, clientes, config,wpAPI,firebase_connection):
    
      self.client_xvideos   = clientes.get('xvideos')
      self.client_xnxx      = clientes.get('xnxx')
      self.client_pornhub   = clientes.get('pornhub')
      self.client_spankbang = clientes.get('spankbang')
      self.client_eporner   = clientes.get('eporner')
      self.client_sex       = clientes.get('sex')
      self.client_hqporner  = clientes.get('hqporner')
      
      self.config = config
      self.total_added = 0
      self.attempt = 1
      self.rounds = {}
      self.wpController = wpAPI
      self.firebase_connection = firebase_connection

  def setConfig(self,config):
    self.config = config

  def format_key(self, string):
      return re.sub(r'[^a-zA-Z0-9_]', '_', string).strip('_') or 'default_key'

  def search_and_add_videos(self):
      multiplier = 1
      while True:
          qty_search = self.config.search_qty * multiplier
          term_results = {}
          total_added_tentativa = 0
          for term in self.config.terms:
              print(f"\n- Pesquisa por: {term}")
              videos = self.client_xvideos.search(term)
              titles = []
              videolist = []
              for _,video in zip(range(qty_search), videos):
                try:
                  titles.append(video.title)
                  video_obj = xvideosVideo(xv_origin=video)
                  print(video_obj.title)
                  videolist.append(video_obj.video)
                except Exception as e:
                  print(f"Erro ao criar video '{video.title}': {e}")
              term_results[self.format_key(term)] = titles
              total_added_tentativa += self.wpController.add_videos(videolist)
              self.total_added += total_added_tentativa
              if self.total_added >= self.config.min_daily:
                self.final_report()
                return

          self.rounds[f'rodada{self.attempt}'] = {
              'qty_adicionado': total_added_tentativa,
              'qty_videos_analisados': len(videolist),
              'termos': term_results,
          }

          if self.attempt >= self.config.max_attempts:
              self.final_report()
              break
          else:
              multiplier *= 2
              self.attempt += 1

  def add_a_video(self, urlvideo):
    videolist = []
    video = self.client_xvideos.get_video(urlvideo)
    video_obj = xvideosVideo(xv_origin=video)
    print(video_obj.title)
    videolist.append(video_obj.video)
    self.wpController.add_videos(videolist)

  def final_report(self):
      print(f'\n---\nResultado Final:\n    -Minimo Necessario: {self.config.min_daily}\n    -Qty Tentativas: {self.attempt}\n    -Qty total de Videos Adicionados: {self.total_added}\n---\n')
      final_result = {
          'configs': vars(self.config),
          'total_added': self.total_added,
          'qty_tentativas': self.attempt,
          'rodadas': self.rounds
      }
      self.firebase_connection.report(final_result)