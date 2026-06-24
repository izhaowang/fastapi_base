'''
创建数据库异步引擎去创建数据库，创建表
'''
from datetime import datetime
from sqlalchemy import func, DateTime, String, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# aiomysql 数据库引擎
dataBaseUrl = "mysql+aiomysql://root:root1234@localhost:3306/fastapi_test?charset=utf8&auth_plugin=mysql_native_password"
#创建异步引擎
async_engine: AsyncEngine = create_async_engine(
    dataBaseUrl,
    echo=True, #可选输出SQl日志
    pool_size=10, #设置连接池中保持持久的链接数
    max_overflow=20 #设置连接池允许建立额外链接数
)



# 创建基类，表对应的模型类
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default= func.now(), default=func.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default= func.now(), default=func.now, comment="更新时间")

class Book(Base):
    # 表名
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True, comment="主键")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, comment="主键")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码(应存储哈希值)")

# 建表：定义函数建表 + FastApi 启动时需要调用建表的函数
async def create_tables():
    # h获取异步引擎，创建事务 建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Base 模型类元素数据