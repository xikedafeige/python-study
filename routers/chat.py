# 从 FastAPI 导入 APIRouter，用来创建一组聊天相关接口。
from fastapi import APIRouter
# 从 FastAPI 导入 StreamingResponse，用来把模型回复一段段返回给浏览器。
from fastapi.responses import StreamingResponse
# 从 LangChain 导入 AIMessage，用来表示历史记录中的 AI 回复。
from langchain_core.messages import AIMessage
# 从 LangChain 导入 HumanMessage，用来表示用户输入的问题。
from langchain_core.messages import HumanMessage
# 从 LangChain 导入 SystemMessage，用来表示系统提示词。
from langchain_core.messages import SystemMessage
# 从 langchain-qwq 导入 ChatQwen，这是通义千问的 LangChain 聊天模型类。
from langchain_qwq import ChatQwen

# 从 config.py 中导入 API Key 和模型服务基础地址。
from config import API_KEY, BASE_URL
# 从 schemas.py 中导入请求体模型 ChatRequest。
from schemas import ChatRequest

# 创建路由对象，并统一给本文件里的接口加上 /api/ai 前缀。
router = APIRouter(prefix="/api/ai", tags=["AI"])


# 定义函数：把前端传来的 history 列表转换成 LangChain 能识别的消息对象。
def build_history_messages(history: list):
    # 创建一个空列表，用来保存转换后的 LangChain 消息对象。
    messages = []
    # 遍历前端传来的每一条历史消息。
    for item in history:
        # 读取这一条历史消息的角色，比如 user 或 assistant。
        role = item.get("role")
        # 读取这一条历史消息的文本内容，如果没有内容就用空字符串。
        content = item.get("content", "")
        # 如果角色是 user，说明这是用户之前说过的话。
        if role == "user":
            # 把用户消息转换成 LangChain 的 HumanMessage。
            messages.append(HumanMessage(content=content))
        # 如果角色是 assistant，说明这是 AI 之前回复过的话。
        elif role == "assistant":
            # 把 AI 消息转换成 LangChain 的 AIMessage。
            messages.append(AIMessage(content=content))
    # 返回转换好的历史消息列表。
    return messages


# 定义生成器函数：调用 LangChain 模型，并持续产出回复文本片段。
def langchain_stream_generator(user_msg: str, history: list):
    # 如果没有读取到 API Key，就直接返回错误提示。
    if not API_KEY:
        # yield 会把这段文字作为流式响应的一部分返回给前端。
        yield "AI reply failed: missing QIANWEN_API_KEY in .env."
        # return 用来结束生成器，不再继续调用模型。
        return

    # 创建 ChatQwen 模型对象，这一步相当于告诉 LangChain 要用哪个模型服务。
    model = ChatQwen(
        # 指定模型名称，这里继续使用当前项目原本使用的 qwen-turbo。
        model="qwen-turbo",
        # 把 .env 中读取到的 API Key 传给模型对象。
        api_key=API_KEY,
        # 把 DashScope 的 OpenAI 兼容接口地址传给模型对象。
        base_url=BASE_URL,
        # 设置本次请求的超时时间，避免网络卡住太久。
        timeout=60,
    )

    # 创建消息列表，第一条是系统提示词，用来设定 AI 的基本行为。
    messages = [SystemMessage(content="You are a helpful AI assistant.")]
    # 把前端传来的历史对话转换成 LangChain 消息，并追加到 messages 里。
    messages.extend(build_history_messages(history))
    # 把用户这一次的新问题追加到 messages 末尾。
    messages.append(HumanMessage(content=user_msg))

    # try 用来捕获 LangChain 或网络调用过程中可能出现的异常。
    try:
        # model.stream 会以流式方式返回模型生成的多个 chunk。
        for chunk in model.stream(messages):
            # 从当前 chunk 中取出文本内容。
            content = chunk.content
            # 有些 chunk 可能没有文本内容，所以这里先判断是否为空。
            if content:
                # 把这一小段文本返回给 StreamingResponse，再由浏览器逐段接收。
                yield content
    # 捕获所有异常，并把错误信息返回给前端，方便学习时直接看到原因。
    except Exception as exc:
        # 把异常内容转成字符串并返回。
        yield f"AI reply failed: {exc}"


# 定义 POST /api/ai/real_stream 接口，前端 test.html 会调用这个地址。
@router.post("/real_stream")
# 定义接口处理函数，req 是 FastAPI 根据 ChatRequest 自动解析出来的请求体。
async def real_ai_chat(req: ChatRequest):
    # 返回 StreamingResponse，让浏览器可以边接收边显示 AI 回复。
    return StreamingResponse(
        # 把用户问题和历史记录交给 LangChain 流式生成器。
        langchain_stream_generator(req.message, req.history),
        # 指定响应类型是 text/event-stream，适合流式文本返回。
        media_type="text/event-stream",
        # 告诉浏览器不要缓存这次流式接口响应。
        headers={"Cache-Control": "no-cache"},
    )
