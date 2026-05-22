# 修正后的代码
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import requests
import json
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()
API_KEY = os.getenv("QIANWEN_API_KEY")  # 注意：阿里云DashScope只需要API_KEY

# 1. 创建应用
app = FastAPI(title="真实AI流式聊天接口")

# 2. 跨域设置（必须）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 前端请求格式
class ChatRequest(BaseModel):
    message: str
    history: list = []  # 支持多轮对话（可选）

# 4. ✅ 修正后的流式生成器
async def real_ai_stream_generator(user_msg: str, history: list):
    """对接通义千问大模型，获取流式智能回复"""
    
    # 构建对话历史
    messages = [
        {"role": "system", "content": "你是一个友好的AI助手，前端转AI工程师的专家"}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_msg})
    
    # 阿里云DashScope API请求
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "qwen-turbo",  # 或 qwen-max
        "messages": messages,
        "stream": True,
        "temperature": 0.7
    }
    
    try:
        # 发起流式请求
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    # 处理SSE格式
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉"data: "前缀
                        
                        if data == "[DONE]":
                            break
                            
                        try:
                            json_data = json.loads(data)
                            if "choices" in json_data and len(json_data["choices"]) > 0:
                                delta = json_data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                            
    except Exception as e:
        yield f"❌ AI回复出错：{str(e)}"

# 5. 流式聊天接口（POST）
@app.post("/api/ai/real_stream")
async def real_ai_chat(req: ChatRequest):
    """真正的AI流式聊天接口"""
    return StreamingResponse(
        real_ai_stream_generator(req.message, req.history),
        media_type="text/event-stream"
    )

# 测试接口
@app.get("/")
def home():
    return {"status": "ok", "message": "请用前端页面测试真实AI流式接口"}