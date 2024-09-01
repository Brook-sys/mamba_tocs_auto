import re
import unicodedata


class Video:
  def __init__(self,title='',thumb='',duration=120,embed='',video_url='',trailer_url='',xv_url='',tags=[]) -> None:
     self.title = title
     self.embed_url = embed
     self.slug = self.tranform_str(self.title)
     self.video_url = video_url
     self.thumbnail_url = thumb
     self.trailer_url = trailer_url if trailer_url else self.convert_thumb_to_vid(self.thumbnail_url)
     self.length = self.time_xv_to_sec(duration)
     self.url = xv_url
     self.id = self.extract_id_from_iframe(self.embed_url)
     self.tags = tags

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

  def convert_thumb_to_vid(self,url):
    base_url = re.sub(r'/thumbs(169)?(xnxx)?((l*)|(poster))/', '/videopreview/', url[:url.rfind("/")])
    return re.sub(r'(-\d+)_([\d]+)', r'_\2\1', base_url) + "_169.mp4"

  def extract_id_from_iframe(self,iframe_string):
    match = re.search(r'https://www\.xvideos\.com/embedframe/([^"]+)', iframe_string)
    return match.group(1) if match else ''

class SearchConfig:
  def __init__(self,firevalues, defaultValues):
    if not firevalues:
      self.terms = defaultValues.get('termos')
      self.min_daily = defaultValues.get('minimoDiario')
      self.search_qty = defaultValues.get('qtyPorTermo')
      self.max_attempts = defaultValues.get('maxTentativas')
    else:
      self.terms = firevalues.get('termos')
      self.min_daily = firevalues.get('minimoDiario')
      self.search_qty = firevalues.get('qtyPorTermo')
      self.max_attempts = firevalues.get('maxTentativas')

class VideoSearcher:
  def __init__(self, client, config,wpAPI,firebase_connection):
      self.client = client
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
          videolist = []
          term_results = {}

          for term in self.config.terms:
              print(f"\n- Pesquisa por: {term}")
              videos = self.client.search(term)
              titles = []
              for _,video in zip(range(qty_search), videos):
                #print(video.title)
                titles.append(video.title)

                video_obj = Video(
                  title=video.title,
                  thumb=video.thumbnail_url,
                  duration=video.length,
                  embed=video.embed_url,
                  xv_url=video.url,
                  tags=video.tags,
                  )
                print(video_obj.title)
                videolist.append(video_obj)


              term_results[self.format_key(term)] = titles

          total_added_tentativa = self.wpController.add_videos(videolist)
          self.total_added += total_added_tentativa

          print(f'\n---\nResultado Rodada:\n   -Videos: {len(videolist)}\n   -Adicionados: {total_added_tentativa}\n---\n')

          self.rounds[f'rodada{self.attempt}'] = {
              'qty_adicionado': total_added_tentativa,
              'qty_videos_analisados': len(videolist),
              'termos': term_results,
          }

          if self.total_added >= self.config.min_daily or self.attempt >= self.config.max_attempts:
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