
from llama_index.llms.groq import Groq
import os
from xvideos_api.xvideos_api import Client as clientxvideos
from xnxx_api import Client as clientxnxx
from firebase_connection import FirebaseConnection
from wordpress_controller import WordpressAPI
from video_processing import VideoSearcher, SearchConfig
from dotenv import load_dotenv

load_dotenv()

llm = Groq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


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
        'maxTentativas':6,
        'sites':{
            'xvideos':True,
            'xnxx':True,
            'pornhub':False,
            'spankbang':False,
            'eporner':False,
            'sex':False,
            'hqporner':False
        } 
    }
)
clientes = {
    'xvideos':clientxvideos(),
    'xnxx':clientxnxx(),
}

video_searcher = VideoSearcher(clientes, default_config,wpAPI,firebase_connection)
video_searcher.search_and_add_videos()