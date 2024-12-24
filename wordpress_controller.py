import requests
import base64
import time
class WordpressAPI:
  def __init__(self,url,user,password) -> None:
    self.wordpress_credentials = user + ':' + password
    self.wordpress_token = base64.b64encode(self.wordpress_credentials.encode())
    self.wordpress_header = {'Authorization': 'Basic ' + self.wordpress_token.decode('utf-8')}
    self.url = url if '/wp-json/wp/v2' in url else url + '/wp-json/wp/v2'
    self.epposts = self.url + '/posts'
    self.eptags = self.url + '/tags'
    self.epmedia = self.url + '/media'

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
    if retries >= 4:
      print('Erro ao obter total de páginas. Máximo de tentativas excedido.')
      return None
    else:
      retries += 1
    try:
        response = requests.get(self.epposts, timeout=10)
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
    while True:
        response = requests.get(f"{self.epposts}?per_page={per_page}&page={page}")
        if response.status_code != 200:
            print(f"Failed to retrieve posts. Status code: {response.status_code}")
            time.sleep(2)
        else:
          response_json = response.json()
          posts.extend(response_json)
          print(f"Posts obtidos na página {page}: {len(response_json)}")
          if page >= total_pages:
              break
          page += 1
          time.sleep(0.5)  # Ajuste conforme necessário
    print(f"Total de posts obtidos: {len(posts)}")
    return posts 

  def __create_video(self,video):

    tags = []
    for tag in video.tags:
      tags.append(self.get_tag_id_by_name(tag))

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
        'xv_id'           : video.id,
        'schema_embed'    : video.embed_url,
        'schema_duration' : f'PT{video.length}S',

        },}

    response = requests.post(self.epposts,headers=self.wordpress_header, json=data)
    if response.status_code == 201:
      print(f'\n✅ Video Adicionado \n   titulo-xv: {video.title} -- url-xv: {video.url}')
      return True
    else:
      print(f'Erro  + {dict(video)}')
      raise Exception("Video Não Adicionado")

  def get_tag_id_by_name(self,tag_name:str):
    params = {"search": tag_name}
    response = requests.get(self.eptags, headers=self.wordpress_header, json=params)
    if response.status_code == 200:
        tags = response.json()
        for tag in tags:
          if tag['name'].lower() == tag_name.lower():
            return tag['id']
        data = {"name": tag_name}
        create_response = requests.post(self.eptags, json=data, headers=self.wordpress_header)
        if create_response.status_code == 201:
            return create_response.json()['id']

  def add_videos(self,videos:list):
    vidExists = self.get_wp_posts()
    idExists = [video.get('meta', {}).get('xv_id') for video in vidExists]
    qty_vids_added = 0
    for video in videos:
      try:
        if video.id in idExists:
          allvidsfilter = {video.get('meta', {}).get('xv_id'): video for video in vidExists}
          thevid = allvidsfilter.get(video.id)
          print(f'\n❌ Não Adicionado pois ja consta \n   titulo-xv: {video.title} -- url-xv: {video.url} \n   titulo-wp: {thevid.get("title").get("rendered")} -- url-wp: {thevid.get("link")}')
        else:
          video.getIaTexts()
          if self.__create_video(video):
            qty_vids_added +=1
      except Exception as e:
        print(f'\n❌❌❌ Não Adicionado pois ocorreu um erro \n{e}\n   titulo-xv: {video.title} -- url-xv: {video.url} ')
    return qty_vids_added