import json
import re
import unicodedata
import time
from llama_index.llms.groq import Groq
import sys
import requests
import os
from generalConfigs import DefaultValues,EnvValues
from wordpress_controller import WordpressAPI
from firebase_connection import FirebaseConnection

inColab = "google.colab" in sys.modules
userdata= None
if inColab:
  userdata = __import__('google.colab.userdata', fromlist=['userdata'])
else:
  from dotenv import load_dotenv
  load_dotenv()
groq_api_key = userdata.get("GROQ_API_KEY") if userdata else os.getenv("GROQ_API_KEY")
groq_model = DefaultValues().get('groqModel')
mode = userdata.get('MODE') if userdata else os.getenv('MODE', 'production')

class xvideosVideo:
  def __init__(self,title='',thumb='',duration=0,embed='',video_url='',trailer_url='',xv_url='',tags=[],xv_origin=None):
    self.title = title if title else xv_origin.title
    
    self.slug = self.tranform_str(self.title)
    self.video_url = video_url
    self.thumbnail_url = thumb or xv_origin.thumbnail_url
    self.trailer_url = trailer_url or self.convert_thumb_to_vid(self.thumbnail_url)
    self.length = self.time_xv_to_sec(duration or xv_origin.length)
    self.url = xv_url or xv_origin.url
    self.id = self.extract_id_from_url(self.url)
    self.tags = tags or xv_origin.tags
    self.embed_url = f'https://videoscdn.online/{self.id}'
    embed_xv_cdn = f'<iframe src="{self.embed_url}" frameborder=0 width=510 height=400 scrolling=no allowfullscreen=allowfullscreen></iframe>'
    self.embed_iframe = embed if embed else embed_xv_cdn
    self.sitename = 'xvideos'
    
    
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
  
  def __init__(self, title='',embed_url='',embed_iframe='',slug='',video_url='',thumbnail_url='',trailer_url='',length=120,url='',id='',tags=[],sitename='') -> None:
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
    self.sitename = sitename
    
    self.llm = Groq(model=groq_model, api_key=groq_api_key)
    self.desc = ''
    self.meta_desc = ''
    self.image_alt = ''
    self.keywords = ''
    
  def getIaTexts(self):
    
    with open("localprompts.json", "r") as f:
        prompts = json.load(f)
    try:
        print(f"\nGerando textos por IA para o video: {self.title}")
        self.desc       = self.exec_prompt(prompts["descricao"].format(titulo=self.title, tags=str(self.tags)),texto='Descrição')
        self.title      = self.exec_prompt(prompts["titulo"].format(titulo=self.title, tags=str(self.tags)),texto='Titulo')
        self.meta_desc  = self.exec_prompt(prompts["meta_descricao"].format(titulo=self.title, descricao=self.desc),texto='Meta descrição')
        self.image_alt  = self.exec_prompt(prompts["imagem_alt"].format(titulo=self.title, tags=str(self.tags)),texto='Descrição da imagem')
        self.keywords   = self.exec_prompt(prompts["palavras_chave"].format(titulo=self.title, tags=str(self.tags)),texto='Palavras chave')
        print(f"\r✅ Textos criados com Sucesso!!!")
        #print(f'\n\n------\n\n{self.title}\n\n{self.desc}\n\n{self.meta_desc}\n\n{self.image_alt}\n\n{self.keywords}\n\n------\n\n')
    except Exception as e:
        print(f"Erro na chamada da API: {e}")
        time.sleep(60) # Pausa de 1 minuto em caso de erro
        return self.getIaTexts() 

  def exec_prompt(self,prompt,texto=''):
    print(f"\rCriando {texto}...", end="")
    time.sleep(2)
    return str(self.llm.complete(prompt)).replace('"','').replace("'","")
class SearchConfig:
  def __init__(self,firevalues=None):
    self.source             = firevalues or DefaultValues().defaultvalues
    self.terms              = self.source.get('termos')
    self.min_daily          = self.source.get('minimoDiario')
    self.search_qty         = self.source.get('qtyPorTermo')
    self.max_attempts       = self.source.get('maxTentativas')

class VideoSearcher:
  def __init__(self, clientes):

      self.env_values = EnvValues()
      self.def_values = DefaultValues()
      
      self.wpController = WordpressAPI(
                                        url       = self.env_values.wpurl,
                                        user      = self.env_values.wpuser,
                                        password  = self.env_values.wppass)
      
      fb_values = self.def_values.get('firebaseValues')
      self.firebase_connection = FirebaseConnection(
                                                      service_key = fb_values.get('keyFile'),
                                                      db_url      = fb_values.get('databaseURL'),
                                                      app_name    = fb_values.get('appName'))
      
      self.config = SearchConfig(self.firebase_connection.getOnlineValues())
      
      self.client_xvideos   = clientes.get('xvideos')
      self.client_xnxx      = clientes.get('xnxx')
      self.client_pornhub   = clientes.get('pornhub')
      self.client_spankbang = clientes.get('spankbang')
      self.client_eporner   = clientes.get('eporner')
      self.client_sex       = clientes.get('sex')
      self.client_hqporner  = clientes.get('hqporner')
      
      self.total_added = 0
      self.attempt = 1
      self.rounds = {}
      
      

  def setConfig(self,config):
    self.config = config

  def format_key(self, string):
      return re.sub(r'[^a-zA-Z0-9_]', '_', string).strip('_') or 'default_key'

  def search_and_add_videos(self):
      multiplier = 1
      videolist = []
      while True:
          qty_search = self.config.search_qty * multiplier
          for term in self.config.terms:
              print(f"\n- Pesquisa por: {term}")
              videos = self.client_xvideos.search(term)
              for _,video in zip(range(qty_search), videos):
                try:
                  video_obj = xvideosVideo(xv_origin=video)
                  if self.wpController.verifyVideoExists(video_obj.video):
                    print(f"Video ja existente: {video_obj.title}")
                  else:
                    videolist.append(video_obj.video)
                    print(f"{len(videolist)}º Video para adicionar: {video_obj.title}")
                except Exception as e:
                  print(f"\n❌❌❌ Erro ao gerar objeto de video '{video.title}': {e}")
                  
                if len(videolist) >= self.config.min_daily:
                  self.wpController.add_videos(videolist)
                  self.total_added = len(videolist)
                  self.final_report()
                  return
          else:
              multiplier *= 2
              self.attempt += 1

  def add_a_video(self, urlvideo):
    videolist = []
    video = self.client_xvideos.get_video(urlvideo)
    video_obj = xvideosVideo(xv_origin=video)
    print(video_obj.title)
    if self.wpController.verifyVideoExists(video_obj.video):
        print(f"Video ja existente: {video_obj.title}")
        
    else:
      videolist.append(video_obj.video)
      self.wpController.add_videos(videolist)

  def final_report(self):
      print(f'\n---\nResultado Final:\n    -Minimo Necessario: {self.config.min_daily}\n    -Qty Tentativas: {self.attempt}\n    -Qty total de Videos Adicionados: {self.total_added}\n---\n')
      final_result = {
          'configs'         : vars(self.config),
          'total_added'     : self.total_added,
          'qty_tentativas'  : self.attempt
      }
      #self.firebase_connection.report(final_result)
  
  def getvideolink(self,idvideo):
    response = requests.get(f'https://www.xvideos.com/embedframe/{idvideo}')
    link = response.text.split("html5player.setVideoURL('/")[1].split("');")[0]
    link = f'https://xvideos.com/{link}'
    print(link)
    rr = requests.get(link)
    if rr.status_code == 200:
      return link
    else:
      return None
  
  def update_all_text_videos(self):
    
    
    for video in self.wpController.allVideos:
      video_id = video['meta']['xv_id'] or video['meta']['porn_site_id']
      
      
      rev = video['meta']['rev']
      if not rev or rev < 2:
        
        time.sleep(1)
        url = self.getvideolink(video_id)
        print(video_id)
        if url:
          vid = self.client_xvideos.get_video(url)
          viddd = xvideosVideo(xv_origin=vid)
          vidd = viddd.video	
          vidd.getIaTexts()
          post_id = video['id']
          sub_nc = video["content"]["rendered"].split('\" alt=\"')[0]
          newcontent = f'{sub_nc}\" alt=\"{vidd.image_alt}"> <br> <p style="text-align: center;">{vidd.desc}</p><br>'
          novos_dados = {
            'title'   : vidd.title,
            'content' : newcontent,
            'meta':
              { 'description'   : vidd.meta_desc,
                'keywords'      : vidd.keywords,
                'rev'           : 2,
                'porn_site_url' : url
                }}
          post_atualizado = self.wpController.atualizar_post(post_id, novos_dados)
          if post_atualizado:
              print(f"Post {post_id} atualizado com sucesso!")
          else:
              print(f"Falha ao atualizar o post {post_id}.")
        else:
          print(f'Erro ao obter link do video {video_id}')
      else:
        print(f'Nada para atualizar no post: {video["id"]}')