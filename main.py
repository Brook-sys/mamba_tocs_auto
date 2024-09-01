
from llama_index.llms.groq import Groq
import os
from xvideos_api.xvideos_api import Client

from firebase_connection import FirebaseConnection
from wordpress_controller import WordpressAPI
from video_processing import VideoSearcher, SearchConfig
from dotenv import load_dotenv

load_dotenv()

llm = Groq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
client_xvideos = Client()

wpurl = 'https://testes-wp.coroasafadas.com.br/'
wpuser = 'admin'
wppass = os.getenv("WORDPRESS_PASS")
wpAPI = WordpressAPI(wpurl,wpuser,wppass,llm)


firebase_connection = FirebaseConnection('servicekey.json', 'https://alimentsite-86639-default-rtdb.firebaseio.com/', 'connsite')

default_config = SearchConfig(
    firevalues    = firebase_connection.getOnlineValues(),
    defaultValues = {
        'termos':['coroas', 'coroa', 'madura', 'madura amadora', 'madura rica'],
        'minimoDiario':2,
        'qtyPorTermo':1,
        'maxTentativas':6 
    }

)

video_searcher = VideoSearcher(client_xvideos, default_config,wpAPI,firebase_connection)
video_searcher.search_and_add_videos()