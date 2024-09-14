import re
import unicodedata
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
    self.embed_url = f'https://videoscdn.net/player/?id={self.id}'
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
    self.getIaTexts() if not mode == 'debug' else None
    
  def getIaTexts(self):
    
    self.desc = str(self.llm.complete(f"crie uma descrição para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, seja original e tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{self.title}' e nas tags {str(self.tags)} apenas mostre a descrição sem conteudos adicionais")).replace('"','').replace("'","")
    self.title = str(self.llm.complete(f"crie um titulo novo diferente do original para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo original: '{self.title}' e nas tags {str(self.tags)} apenas mostre o titulo gerado sem conteudos adicionais")).replace('"','').replace("'","")
    self.meta_desc = str(self.llm.complete(f"crie uma meta descrição para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{str(self.title)}' e no conteudo {str(self.desc)} apenas mostre a meta descrição gerada sem conteudos adicionais")).replace('"','').replace("'","")
    self.image_alt = str(self.llm.complete(f"crie uma descrição para uma imagem para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{str(self.title)}' e nas tags {str(self.tags)} apenas mostre a descrição de video gerada sem conteudos adicionais")).replace('"','').replace("'","")
    self.keywords = str(self.llm.complete(f"crie de 3 a 10 palavras-chave separados por virgula para um video adulto tendo em vista SEO para ranquear melhor no google como um site de videos de coroas, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{str(self.title)}' e nas tags {str(self.tags)} apenas mostre as palavras-chave geradas separados por virgula  sem conteudos adicionais")).replace('"','').replace("'","")

class SearchConfig:
  def __init__(self,firevalues, defaultValues):
    source = firevalues or defaultValues
    source = defaultValues if mode == 'debug' else source

    self.terms          = source.get('termos')
    self.min_daily      = source.get('minimoDiario')
    self.search_qty     = source.get('qtyPorTermo')
    self.max_attempts   = source.get('maxTentativas')

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
                titles.append(video.title)
                video_obj = xvideosVideo(xv_origin=video)
                print(video_obj.title)
                videolist.append(video_obj.video)
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

  def final_report(self):
      print(f'\n---\nResultado Final:\n    -Minimo Necessario: {self.config.min_daily}\n    -Qty Tentativas: {self.attempt}\n    -Qty total de Videos Adicionados: {self.total_added}\n---\n')
      final_result = {
          'configs': vars(self.config),
          'total_added': self.total_added,
          'qty_tentativas': self.attempt,
          'rodadas': self.rounds
      }
      self.firebase_connection.report(final_result)