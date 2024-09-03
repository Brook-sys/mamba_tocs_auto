
from llama_index.llms.groq import Groq
import os
from xvideos_api.xvideos_api import Client as clientxvideos
#from xnxx_api import Client as clientxnxx
from firebase_connection import FirebaseConnection
from wordpress_controller import WordpressAPI
from video_processing import VideoSearcher, SearchConfig
from dotenv import load_dotenv

load_dotenv()

llm = Groq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


wpurl = 'https://coroasafadas.com.br/'
wpuser = 'zeroescobar9'
wppass = os.getenv("WP_PRODUCAO")
wpAPI = WordpressAPI(wpurl,wpuser,wppass,llm)


firebase_connection = FirebaseConnection('servicekey.json', 'https://alimentsite-86639-default-rtdb.firebaseio.com/', 'connsite')

default_config = SearchConfig(
    firevalues    = firebase_connection.getOnlineValues(),
    defaultValues = {
        'termos':['coroa gostosa','madura','madura amador','madura rica','cougar','coroa peituda','cougar slutty','madura culona','madura tetona'],
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
    #'xnxx':clientxnxx(),
}

video_searcher = VideoSearcher(clientes, default_config,wpAPI,firebase_connection)
video_searcher.search_and_add_videos()