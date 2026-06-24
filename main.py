from sys import prefix

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager  # 1. 导入 asynccontextmanager
from apps.app01 import app01
from apps.app02 import app02
from apps.app03 import app03
from apps.app04 import app04
from apps.app041 import app041
from apps.app051 import app051
from apps.app061 import app061
from apps.book import book

#导入建表函数
from orm.createa_async_engine import  create_tables



# --- 启动事务：建表
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("数据库已创建")
    yield
    # --- 关闭时执行的代码（可选）---
    # 这里的代码会在应用关闭时执行，例如用于释放资源
    # 例如: await async_engine.dispose()
    print("🛑 应用正在关闭，资源已释放")

# 3. 创建 FastAPI 实例时传入 lifespan 参数
app = FastAPI(lifespan=lifespan)  # 关键修改

# 访问规则 /xxx 表示 statics文件下
# 访问路径/xxx/app.js
app.mount("/xxx", StaticFiles(directory="statics"))
# 路由分发
app.include_router(app01,tags=["路径参数"])
app.include_router(app02,tags=["查询参数"])
app.include_router(app03,tags=["请求体参数"])
app.include_router(app04,tags=["查询参数和字符串参数校验"])
app.include_router(app041,tags=["form表单请求"])
app.include_router(app051,tags=["文件上传请求"])
app.include_router(app061,tags=["request对象"])
app.include_router(book, tags=["数据库增删改查"])

