import os
import sys
from xvideos_api.xvideos_api import Client as clientxvideos
#from xnxx_api import Client as clientxnxx
from firebase_connection import FirebaseConnection
from wordpress_controller import WordpressAPI
from video_processing import VideoSearcher, SearchConfig
import datetime

inColab = "google.colab" in sys.modules
userdata= None
if inColab:
  userdata = __import__('google.colab.userdata', fromlist=['userdata'])
else:
  from dotenv import load_dotenv
  load_dotenv()
groq_api_key = userdata.get("GROQ_API_KEY") if userdata else os.getenv("GROQ_API_KEY")
mode = userdata.get('MODE') if userdata else os.getenv('MODE', 'production') 
prefixMode = "DEBUG" if mode == "debug" else "PROD"
wpuser = userdata.get(f'WP_USER_{prefixMode}') if userdata else os.getenv(f'WP_USER_{prefixMode}')
wppass = userdata.get(f'WP_PASS_{prefixMode}') if userdata else os.getenv(f'WP_PASS_{prefixMode}')
wpurl = userdata.get(f'WP_URL_{prefixMode}') if userdata else os.getenv(f'WP_URL_{prefixMode}')
init_time = datetime.datetime.now()


print(f"\n-----------------------------------------------\nInicio: {init_time.strftime('%d/%m/%Y %H:%M:%S')}\n", )

wpAPI = WordpressAPI(wpurl,wpuser,wppass)
firebase_connection = FirebaseConnection('servicekey.json', 'https://alimentsite-86639-default-rtdb.firebaseio.com/', 'connsite')

default_config = SearchConfig(
    firevalues    = firebase_connection.getOnlineValues(),
    defaultValues = {
        'termos':['coroa gostosona','madura','madura amador','madura rica','cougar','coroa peituda','cougar slutty','madura culona','madura tetona'],
        'minimoDiario':2,
        'qtyPorTermo':5,
        'maxTentativas':6,
        'sites':{
            'xvideos':True,
            'xnxx':False,
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
#video_searcher.add_a_video("")
end_time = datetime.datetime.now()
print(f"\nTermino:{end_time.strftime('%d/%m/%Y %H:%M:%S')}\n-----------------------------------------------\n", )
