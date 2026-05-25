# 从 typing 导入 Dict 和 List，用来给字段写类型提示。
from typing import Dict, List

# 从 pydantic 导入 BaseModel，用来定义请求体的数据结构。
from pydantic import BaseModel


# 定义前端调用 /api/ai/real_stream 时传入的 JSON 格式。
class ChatRequest(BaseModel):
    # message 保存用户这一次输入的问题。
    message: str
    # history 保存历史对话，默认是空列表。
    history: List[Dict] = []
