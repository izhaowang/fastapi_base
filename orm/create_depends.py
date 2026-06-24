'''
创建异步会话工厂
创建依赖项--用于读取数据库会话
然后将依赖项注入到 fastApi 路由函数去对数据库进行增删改查
'''
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from orm.createa_async_engine import async_engine

##创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind= async_engine, # 绑定数据库引擎
    class_= AsyncSession, # 指定会话类
    expire_on_commit= False #提交后会话不过期， 不会重新查看数据库
)
# 创建依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session #返回数据库会话给路由处理函数
            await  session.commit() #提交事务
        except Exception:
            await session.rollback() #有异常回滚食物
            raise
        finally:
            await session.close() # 关闭会话