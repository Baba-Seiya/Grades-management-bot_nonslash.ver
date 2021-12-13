# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv
load_dotenv(".env")

# 環境変数を参照
import os
MY_TOKEN = os.getenv('MY_TOKEN')