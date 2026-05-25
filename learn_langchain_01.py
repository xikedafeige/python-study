# 从 LangChain 导入 HumanMessage，用来表示用户输入。
from langchain_core.messages import HumanMessage
# 从 LangChain 导入 SystemMessage，用来表示系统提示词。
from langchain_core.messages import SystemMessage
# 从 langchain-qwq 导入 ChatQwen，用来调用通义千问聊天模型。
from langchain_qwq import ChatQwen

# 从 config.py 中读取 API Key 和模型服务基础地址。
from config import API_KEY, BASE_URL


# 定义程序入口函数，方便以后扩展更多学习代码。
def main():
    # 判断 API Key 是否存在，避免没有配置时直接请求失败。
    if not API_KEY:
        # 打印清晰的错误提示，告诉你应该检查 .env 文件。
        print("缺少 QIANWEN_API_KEY，请先检查 .env 文件。")
        # 结束函数，不再继续执行模型调用。
        return

    # 创建 ChatQwen 模型对象，这是 LangChain 调用通义千问的入口。
    model = ChatQwen(
        # 指定要调用的模型名称。
        model="qwen-turbo",
        # 传入 DashScope API Key。
        api_key=API_KEY,
        # 传入 DashScope OpenAI 兼容接口地址。
        base_url=BASE_URL,
        # 设置请求超时时间，避免网络异常时一直等待。
        timeout=60,
    )

    # 创建 messages 列表，LangChain 的聊天模型使用消息列表作为输入。
    messages = [
        # SystemMessage 用来告诉 AI 它应该扮演什么角色。
        SystemMessage(content="You are a helpful AI assistant."),
        # HumanMessage 用来表示用户真正提出的问题。
        HumanMessage(content="请用一句话解释 LangChain 是什么。"),
    ]

    # 调用 invoke 发送一次普通非流式请求，并等待完整回复。
    response = model.invoke(messages)
    # 打印 AI 回复的纯文本内容。
    print(response.content)


# 判断当前文件是否是被直接运行，而不是被其他文件导入。
if __name__ == "__main__":
    # 直接运行本文件时，调用 main 函数。
    main()
