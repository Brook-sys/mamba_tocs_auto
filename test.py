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
print(wpuser)