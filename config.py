# config.py
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("QIANWEN_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
PORT = 8000