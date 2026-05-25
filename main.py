# 导入 FastAPI 类，用来创建后端应用对象。
from fastapi import FastAPI
# 导入 CORS 中间件，用来允许浏览器跨域访问后端接口。
from fastapi.middleware.cors import CORSMiddleware
# 从 routers 包里导入 chat 模块，里面保存聊天相关路由。
from routers import chat

# 创建 FastAPI 应用实例，后续所有接口都会挂到这个 app 上。
app = FastAPI()

# 给 app 添加跨域中间件，让 test.html 这种本地页面可以请求后端。
app.add_middleware(
    # 指定要添加的中间件类型是 CORSMiddleware。
    CORSMiddleware,
    # 允许任意来源访问接口，学习项目里这样配置最简单。
    allow_origins=["*"],
    # 允许任意 HTTP 方法，比如 GET、POST、OPTIONS。
    allow_methods=["*"],
    # 允许任意请求头，比如 Content-Type。
    allow_headers=["*"],
)

# 把 chat.py 中定义的路由挂载到主应用上。
app.include_router(chat.router)

# 定义一个根路径 GET 接口，用来快速确认服务是否启动。
@app.get("/")
# 定义根路径接口的处理函数。
def index():
    # 返回一个简单 JSON，浏览器访问 http://127.0.0.1:8000/ 时会看到它。
    return {"msg": "模块化项目启动成功"}
