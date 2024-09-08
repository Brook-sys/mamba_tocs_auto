
from llama_index.llms.groq import Groq
import os
import sys
from xvideos_api.xvideos_api import Client as clientxvideos
#from xnxx_api import Client as clientxnxx
from firebase_connection import FirebaseConnection
from wordpress_controller import WordpressAPI
from video_processing import VideoSearcher, SearchConfig
from dotenv import load_dotenv
load_dotenv()


inColab = "google.colab" in sys.modules
mode = os.getenv('MODE', 'production') 

userdata = __import__('google.colab.userdata', fromlist=['userdata']) if inColab else None

groq_api_key =os.getenv("GROQ_API_KEY")
prefixMode = "DEBUG" if mode == "debug" else "PROD"

wpuser = userdata.get(f'WP_USER_{prefixMode}') if userdata else os.getenv(f'WP_USER_{prefixMode}')
wppass = userdata.get(f'WP_PASS_{prefixMode}') if userdata else os.getenv(f'WP_PASS_{prefixMode}')
wpurl = userdata.get(f'WP_URL_{prefixMode}') if userdata else os.getenv(f'WP_URL_{prefixMode}')



llm = Groq(model="llama-3.1-70b-versatile", api_key=groq_api_key)
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