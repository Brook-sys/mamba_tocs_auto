import requests
import base64

class WordpressAPI:
  def __init__(self,url,user,password,LLM_groq) -> None:
    self.wordpress_credentials = user + ':' + password
    self.wordpress_token = base64.b64encode(self.wordpress_credentials.encode())
    self.wordpress_header = {'Authorization': 'Basic ' + self.wordpress_token.decode('utf-8')}
    self.url = url if '/wp-json/wp/v2' in url else url + '/wp-json/wp/v2'
    self.epposts = self.url + '/posts'
    self.eptags = self.url + '/tags'
    self.epmedia = self.url + '/media'
    self.llm_groq = LLM_groq

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
        print(f'Imagem hospedada com sucesso: {hosted_image_url}')
        return hosted_image_url, image_data['id']
    else:
        print(f'Erro ao hospedar a imagem: {response.status_code}')
        print(response.text)
        return None


  def get_wp_postsss(self):
    response = requests.get(self.epposts)
    response_json = response.json()
    return response_json

  def get_wp_posts(self):
    posts, page, per_page = [], 1, 100

    while True:
        response = requests.get(f"{self.epposts}?per_page={per_page}&page={page}")
        if response.status_code != 200:
            print(f"Failed to retrieve posts. Status code: {response.status_code}")
            break
        response_json = response.json()
        posts.extend(response_json)
        if len(response_json) < per_page:
            break
        page += 1
    return posts

  def __create_video(self,video):

    tags = []
    for tag in video.tags:
      tags.append(self.get_tag_id_by_name(tag))

    ia_desc = str(self.llm_groq.complete(f"crie uma descrição para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, seja original e tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{video.title}' e nas tags {str(video.tags)} apenas mostre a descrição sem conteudos adicionais")).replace('"','').replace("'","")
    ia_title = str(self.llm_groq.complete(f"crie um titulo novo diferente do original para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo original: '{video.title}' e nas tags {str(video.tags)} apenas mostre o titulo gerado sem conteudos adicionais")).replace('"','').replace("'","")
    ia_meta_desc = str(self.llm_groq.complete(f"crie uma meta descrição para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{str(ia_title)}' e no conteudo {str(ia_desc)} apenas mostre a meta descrição gerada sem conteudos adicionais")).replace('"','').replace("'","")
    ia_image_alt = str(self.llm_groq.complete(f"crie uma descrição para uma imagem para um video adulto tendo em vista SEO(Search Optimization Engine) para ranquear melhor no google como um site de videos de coroas, tente não parecer uma ia, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{str(ia_title)}' e nas tags {str(video.tags)} apenas mostre a descrição de video gerada sem conteudos adicionais")).replace('"','').replace("'","")
    ia_keywords = str(self.llm_groq.complete(f"crie de 3 a 10 palavras-chave separados por virgula para um video adulto tendo em vista SEO para ranquear melhor no google como um site de videos de coroas, escreva de forma vulgar e apelativa para o lado erotico com palavras brasileiras de cunho erotico, com base no titulo: '{str(ia_title)}' e nas tags {str(video.tags)} apenas mostre as palavras-chave geradas separados por virgula  sem conteudos adicionais")).replace('"','').replace("'","")
    
    hosp_thumb, id_thumb = self.postImageLink(video.thumbnail_url,video.id+'_'+video.slug)
    xv_cdn = f'https://videoscdn.net/player/?id={video.id}'
    embed_xv_cdn = f'<iframe src="{xv_cdn}" frameborder=0 width=510 height=400 scrolling=no allowfullscreen=allowfullscreen></iframe>'
    data = {
    'title'           : ia_title,
    'status'          : 'publish',
    'slug'            : video.slug,
    'tags'            : ','.join(map(str,tags)),
    'content'         : f'<img src="{hosp_thumb}" alt="{ia_image_alt}"> <br> <p style="text-align: center;">{ia_desc}</p><br>',
    'format'          : 'video',
    'featured_media'  : id_thumb,


    'meta':{
        'keywords'        : ia_keywords,
        'description'     : ia_meta_desc,
        'embed'           : embed_xv_cdn,
        'video_url'       : video.video_url,
        'trailer_url'     : video.trailer_url,
        'thumb'           : hosp_thumb,
        'duration'        : video.length,
        'xv_id'           : video.id,
        'schema_embed'    : xv_cdn,
        'schema_duration' : f'PT{video.length}S',

        },}

    response = requests.post(self.epposts,headers=self.wordpress_header, json=data)
    if response.status_code == 201:
      print(f'✅ Video Adicionado \n   titulo-xv: {video.title} -- url-xv: {video.url} \n')
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
          print(f'❌ Não Adicionado pois ja consta \n   titulo-xv: {video.title} -- url-xv: {video.url} \n   titulo-wp: {thevid.get("title").get("rendered")} -- url-wp: {thevid.get("link")}\n')
        else:
          if self.__create_video(video):
            qty_vids_added +=1

      except Exception as e:
        print(f'❌❌❌ Não Adicionado pois ocorreu um erro \n{e}\n   titulo-xv: {video.title} -- url-xv: {video.url} ')
    return qty_vids_added