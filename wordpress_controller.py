import requests
import base64
import time
import traceback
from generalConfigs import DefaultValues,EnvValues
class WordpressAPI:
  def __init__(self,url,user,password):
    self.env_values = EnvValues()
    self.def_values = DefaultValues()
    self.max_retries = self.def_values.get('max_retries', {}).get('general', 5)
    self.wordpress_credentials = user + ':' + password
    self.wordpress_token = base64.b64encode(self.wordpress_credentials.encode())
    self.wordpress_header = {'Authorization': 'Basic ' + self.wordpress_token.decode('utf-8')}
    self.url = url if '/wp-json/wp/v2' in url else url + '/wp-json/wp/v2'
    self.epposts = self.url + '/posts'
    self.eptags = self.url + '/tags'
    self.epmedia = self.url + '/media'
    self.allVideosID = ''
    self.allVideos = ''
    self.refreshAllVideos()

  def postImageLink(self,linkimage,nome):

    data = requests.get(linkimage).content

    wp_header_media = self.wordpress_header.copy()
    wp_header_media.update({
        'Content-Disposition': f'attachment; filename="{nome}.jpg"',
        'Content-Type': 'image/jpeg'
    })

    response = requests.post(self.epmedia,headers=wp_header_media,data=data)

    if response.status_code == 201:
        # Obter o link da imagem hospedada no WordPress
        image_data = response.json()
        hosted_image_url = image_data['guid']['rendered']
        print(f'\n✅ Imagem hospedada com sucesso: {hosted_image_url}')
        return hosted_image_url, image_data['id']
    else:
        print(f'\n❌ Erro ao hospedar a imagem: {response.status_code}')
        print(response.text)
        return None

  def identify_duplicate_posts(self):
    posts = self.get_wp_posts()

    unique_posts = {}
    duplicate_posts = []

    for post in posts:
      xv_id = post.get('meta', {}).get('xv_id')
      if not xv_id:
        print('notem')
        continue

      if xv_id not in unique_posts:
        unique_posts[xv_id] = post 
        print(f'unic: {xv_id}')
      else:
        duplicate_posts.append(post)
        print(f'           dupl: {xv_id}')

    for duplicate in duplicate_posts:
      post_id = duplicate['id']
      
      '''
      response = requests.delete(f"{self.epposts}/{post_id}")
      
      if response.status_code == 200:
        print(f"Post com ID {post_id} foi deletado.")
      else:
        print(f"Falha ao deletar o post com ID {post_id}. Status code: {response.status_code}")
      '''
      print(f"Deleção de posts duplicados concluída. Total de duplicados removidos: {len(duplicate_posts)}.")

  def get_wp_postsss(self):
    response = requests.get(self.epposts)
    response_json = response.json()
    return response_json

  def get_wp_total_pages(self,retries=0):
    if retries >= self.max_retries:
      print('Erro ao obter total de páginas. Máximo de tentativas excedido.')
      return None
    else:
      retries += 1
    try:
        response = requests.get(f'{self.epposts}?per_page=100')
        print(f'{self.epposts}?per_page=100')
        response.raise_for_status()  # Lança exceção para erros HTTP
        total_pages_header = response.headers.get('X-WP-TotalPages')
        if not total_pages_header:
            print("Cabeçalho X-WP-TotalPages não encontrado. Verifique a API.")
            raise ValueError
        return int(total_pages_header)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter total de páginas: {e}")
        return self.get_wp_total_pages(retries)
    except ValueError:
        print(f"Cabeçalho X-WP-TotalPages inválido: {response.headers.get('X-WP-TotalPages')}. Verifique a configuração do servidor.")
        return self.get_wp_total_pages(retries)
      
  def get_wp_posts(self):
    posts = []
    page = 1
    per_page = 100
    total_pages = self.get_wp_total_pages()
    print(f"Obtendo posts existentes...")
    while page <= total_pages:
      try:
        print(f'\r{page * 100 / total_pages:.2f}%',end='')
        response = requests.get(f"{self.epposts}?per_page={per_page}&page={page}")
        response.raise_for_status()
        response_json = response.json()
        posts.extend(response_json)
        page += 1
        time.sleep(0.5)
      except Exception as e:
        print(f"Failed to retrieve posts. Status code: {e}")
        time.sleep(2)
          
    print(f"\rTotal de posts existentes: {len(posts)}")
    return posts 

  def __create_video(self,video):
    tags = []
    for tag in video.tags:
      tags.append(self.get_tag_id_by_name(tag))
    return None
    hosp_thumb, id_thumb = self.postImageLink(video.thumbnail_url,video.id+'_'+video.slug)
    data = {
    'title'           : video.title,
    'status'          : 'publish',
    'slug'            : video.slug,
    'tags'            : ','.join(map(str,tags)),
    'content'         : f'<img src="{hosp_thumb}" alt="{video.image_alt}"> <br> <p style="text-align: center;">{video.desc}</p><br>',
    'format'          : 'video',
    'featured_media'  : id_thumb,
    'meta':{
        'keywords'        : video.keywords,
        'description'     : video.meta_desc,
        'embed'           : video.embed_iframe,
        'video_url'       : video.video_url,
        'trailer_url'     : video.trailer_url,
        'thumb'           : hosp_thumb,
        'duration'        : video.length,
        'porn_site'       : video.sitename,
        'porn_site_id'    : video.id,
        'porn_site_url'   : video.url,
        'schema_embed'    : video.embed_url,
        'schema_duration' : f'PT{video.length}S',

        },}

    response = requests.post(self.epposts,headers=self.wordpress_header, json=data)
    if response.status_code == 201:
      return True
    else:
      print(response.text)
      print(response.status_code)
      return False

  def get_tag_id_by_name(self,tag_name:str):
    params = {"search": tag_name}
    response = requests.get(f"{self.eptags}?per_page=100", headers=self.wordpress_header, json=params)
    if response.status_code == 200:
      tags = response.json()
      
      for tag in tags:
        if tag['name'].lower() == tag_name.lower():
          return tag['id']
      data = {"name": tag_name}
      create_response = requests.post(self.eptags, json=data, headers=self.wordpress_header)
      if create_response.status_code == 201:
        return create_response.json()['id']

  def atualizar_post(self,post_id, novos_dados):
    try:
        url = f'{self.epposts}/{post_id}'
        response = requests.post(url,headers=self.wordpress_header, json=novos_dados)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao atualizar post {post_id}: {e}.")
        return None
  def update_all_videos(self):
    
    for video in self.allVideos:
      video_id = video['meta']['xv_id'] or video['meta']['schema_embed'].split('/')[-1] 
      post_id = video['id']
      novo_campo = video['meta']['porn_site_id']
      if not novo_campo:
        novos_dados = {
          'meta':
            {'porn_site_id': video_id,
              'porn_site': 'xvideos'}}
        print(novos_dados)
        post_atualizado = self.atualizar_post(post_id, novos_dados)
        if post_atualizado:
            print(f"Post {post_id} atualizado com sucesso!")
        else:
            print(f"Falha ao atualizar o post {post_id}.")
      else:
        print('nada para atualizar')

  def add_videos(self,videos:list):
    for video in videos:
      try:
        video.getIaTexts()
        if self.__create_video(video):
          print(f'\n✅ Video Adicionado \n   titulo-xv: {video.title} -- url-xv: {video.url}')
        else:
          print(f'\n❌ Erro ao adicionar video \n   titulo-xv: {video.title} -- url-xv: {video.url} ')
      except Exception as e:
        traceback.print_exc()
        print(f'\n❌❌❌ Não Adicionado pois ocorreu um erro \n{e}\n   titulo-xv: {video.title} -- url-xv: {video.url} ')

  def refreshAllVideos(self):
    self.allVideos = self.get_wp_posts()
    self.allVideosID = [video.get('meta', {}).get('porn_site_id') for video in self.allVideos]
  def verifyVideoExists(self,video):
    return video.id in self.allVideosID