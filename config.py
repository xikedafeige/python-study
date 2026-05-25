# 导入 Python 标准库 os，用来读取系统环境变量。
import os

# 导入 load_dotenv，用来把 .env 文件中的配置加载到环境变量里。
from dotenv import load_dotenv

# 执行 .env 加载，这样后面 os.getenv 才能读到 QIANWEN_API_KEY。
load_dotenv()

# 从环境变量中读取阿里云 DashScope API Key。
API_KEY = os.getenv("QIANWEN_API_KEY")
# 配置 DashScope 的 OpenAI 兼容接口基础地址。
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# 配置本地 FastAPI 服务默认端口。
PORT = 8000
