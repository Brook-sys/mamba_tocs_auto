import os
import sys
from xvideos_api.xvideos_api import Client as clientxvideos
#from xnxx_api import Client as clientxnxx
from firebase_connection import FirebaseConnection
from generalConfigs import DefaultValues
from wordpress_controller import WordpressAPI
from video_processing import VideoSearcher, SearchConfig
import datetime
from dotenv import load_dotenv
load_dotenv()



groq_api_key = os.getenv("GROQ_API_KEY")
mode = os.getenv("MODE", "production")
prefix_mode = "DEBUG" if mode == "debug" else "PROD"

wpuser = os.getenv(f'WP_USER_{prefix_mode}')
wppass = os.getenv(f'WP_PASS_{prefix_mode}')
wpurl = os.getenv(f'WP_URL_{prefix_mode}')

init_time = datetime.datetime.now()


print(f"\n-----------------------------------------------\nInicio: {init_time.strftime('%d/%m/%Y %H:%M:%S')}\n", )

clientes = {
    'xvideos':clientxvideos(),
    #'xnxx':clientxnxx(),
}

video_searcher = VideoSearcher(clientes)
#video_searcher.update_all_text_videos()
video_searcher.search_and_add_videos()
#video_searcher.add_a_video("")
end_time = datetime.datetime.now()
print(f"\nTermino: {end_time.strftime('%d/%m/%Y %H:%M:%S')}\n-----------------------------------------------\n", )
