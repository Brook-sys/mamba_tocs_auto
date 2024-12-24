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

def get_env_var(key, default=None):
    return userdata.get(key) if inColab else os.getenv(key, default)

groq_api_key = get_env_var("GROQ_API_KEY")
mode = get_env_var("MODE", "production")
prefix_mode = "DEBUG" if mode == "debug" else "PROD"

wpuser = get_env_var(f'WP_USER_{prefix_mode}')
wppass = get_env_var(f'WP_PASS_{prefix_mode}')
wpurl = get_env_var(f'WP_URL_{prefix_mode}')

init_time = datetime.datetime.now()


print(f"\n-----------------------------------------------\nInicio: {init_time.strftime('%d/%m/%Y %H:%M:%S')}\n", )

wpAPI = WordpressAPI(wpurl,wpuser,wppass)
firebase_connection = FirebaseConnection('servicekey.json', 'https://alimentsite-86639-default-rtdb.firebaseio.com/', 'connsite')

default_config = SearchConfig(firebase_connection.getOnlineValues())

clientes = {
    'xvideos':clientxvideos(),
    #'xnxx':clientxnxx(),
}

video_searcher = VideoSearcher(clientes, default_config,wpAPI,firebase_connection)
video_searcher.search_and_add_videos()
#video_searcher.add_a_video("")
end_time = datetime.datetime.now()
print(f"\nTermino: {end_time.strftime('%d/%m/%Y %H:%M:%S')}\n-----------------------------------------------\n", )
