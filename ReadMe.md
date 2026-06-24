from setuptools.command.develop import developfrom setuptools.command.develop import developfrom sqlite3.dbapi2 import apilevelfrom ctypes import cdll

# 首次创建项目
```python
# 进入目录
cd code
# 创建文件夹
mkdir projName
# 进入文件夹
cd porjName
```
## 创建虚拟环境
```python
# 开始前创建一个虚拟环境 python自带venv模块
python3 -m venv .venv
```
此时项目会会有一个 .venv 文件夹
# 激活虚拟环境 在每一个新终端回话并准备开发项目世 要激活虚拟环境
- macOS / Linux: source .venv/bin/activate 
- Windows (Git Bash): source .venv/Scripts/activate
- Windows (CMD): .venv\Scripts\activate
激活后终端会显示 .venv 表示已经成功进入了独立的沙箱
# 安装依赖, 在激活的环境下 使用pip 安装项目所需的包
```python
pip install fastapi[standard]
```
# 生成requirements.txt 文件
```python
python3 -m pip freeze > requirements.txt
```
# 根据requirements.txt 文件安装依赖
```python
python3 -m pip install -r requirements.txt
```

# 第二次进入｜clone 别人的项目
## 进入目录
```python
cd projName
```
## 创建虚拟环境 参考1
## 激活虚拟环境 参考1
## 根据根据requirements.txt 文件安装依赖
## 运行代码
```python
fastapi dev
打开  http://127.0.0.1:8000
```
# 退出虚拟环境
```python
deactivate
```


# orm
## 概念
orm 是一种映射关系 用于面向对象语言和关系型数据库之间建立映射。 允许开发者通过操作对象的方式与数据库进行交互，并无需编写复杂的sal语句
## 安装 数据库驱动
```python
pip install "sqlalchemy[asyncio]" aiomysql
```
## 建库 建表
+ 创建数据库引擎
```python
from sqlalchemy.ext.asyncio import create_async_engine

dataBaseUrl = "mysql+aiomysql://root:root1234@localhost:3306/fastapi_test?charset=utf8&auth_plugin=mysql_native_password"

#创建异步引擎
async_engine = create_async_engine(
    dataBaseUrl,
    echo=True, #可选输出SQl日志
    pool_size=10, #设置连接池中保持持久的链接数
    max_overflow=20 #设置连接池允许建立额外链接数
)
```
+ 定义模型类
1. 先要有基类
基类继承DeclarativeBase 
2. 模型类 表对应的类
```python

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

```
3. 建表
```python
# 建表：定义函数建表 + FastApi 启动时需要调用建表的函数
async def create_tables():
    # h获取异步引擎，创建事务 建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Base 模型类元素数据
```

```python
from contextlib import asynccontextmanager 
from fastapi import FastAPI
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
```
## 接口中使用orm 增删改查功能
***核心***：创建依赖项，使用Depends 注入到处理函数
首先的有个依赖项， 用于读取数据库会话
因此要先创建会话工厂
+ 创建异步会话工厂
```python
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
```
+ 依赖项用户读取数据库会话
```python
from typing import Optional, Union
from sqlalchemy import select
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from orm.createa_async_engine import Book
from orm.create_depends import get_database
from fastapi import APIRouter
book = APIRouter()

## Depends(get_database) 注入依赖项
@book.get("/book/books")
async def get_books_list(db: AsyncSession = Depends(get_database)):
    # 查询

    result = await db.execute(select(Book))
    book = result.scalars().all()
    return book
```

### 数据库操作-查询
***核心*** await db.execute(select(模型类))， 返回一个ORM对象
```python
result = await db.execute(select(Book))
book = result.scalars().all()
return book
```
+ 获取所有数据
 scalars().all()
+ 获取单条数据
 scalars().first() 提取第一个数据
 scalar_one_or_none() 提取一个或null
 scalar() 提取标量值，配合聚合查询使用
 get(模型类， 主键值)
```python
book = await db.get(Book, book_id)
return book
```
+ 条件查询
scalar_one_or_none 有就是返回 没有返回none
```python
## Book 模型类， id是查询条件
select(Book).where(Book.id == id)
```
比较判断==；>; <; >=; <=等
模糊查询 like（）
与非查询 & ｜ ～
包含查询： in_()

+ 聚合查询 func.方法(模型类.属性)
result = await db.execute(select(func.max(Book.price)))
1. count 同级行数量
2. avg 求平均值
3. max 最大
4. min 最小
5. sum 求和

##### 分页查询
分页：select().offset(offset).limit(size)
offset: 跳过记录数-- = （当前页码-1） * 页面数量
limit: 返回记录数--每页多少条
```python

# 分页查询， 参数在查询参数中 ?page=xx&size=xx
@book.post("/book/search_book")
async def get_search_book_paginated(
        page: int = Query(1, ge=1, description="页码，从1开始"),
        size: int = Query(10, description="每页条数"),
        db: AsyncSession = Depends(get_database)
):
    #计算偏移量
    offset = (page - 1) * size
    # 查询总数
    total_stmt = select(func.count()).select_from(Book)
    total = await db.execute(total_stmt)
    total_count = total.scalar()

    #分页查询
    stmt = select(Book).offset(offset).limit(size)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return {
        "total": total_count,
        "page": page,
        "size": size,
        "data": books
    }

# 请求体分页查询
class PaginationParams(BaseModel):
    page:int = 1
    size:int = 10

@book.post("/book/search_book/page")
async def search_book_page(
    params: PaginationParams,
    db: AsyncSession = Depends(get_database)
):
    offset = (params.page - 1) * params.size
    stmt = select(Book)
    # 查询总数
    count_stmt = select(func.count()).select_from(Book)
    total = await db.execute(count_stmt)
    total_count = total.scalar()

    # 分页查询
    stmt = stmt.offset(offset).limit(params.size)
    result = await db.execute(stmt)
    books = result.scalars().all()

    return {
        "total": total_count,
        "page": params.page,
        "size": params.size,
        "data": books
    }

```
### 数据库操作-新增
核心：定义orm对象-》添加对象到事务：add(对象)-〉commit 提交到数据库
```python
class BookBase(BaseModel):
    id: int
    bookname: str
    author: str
    price: str
    publisher: str
@book.post("/book/add_book", summary="新增书籍")
async def add_book(book: BookBase, db: AsyncSession = Depends(get_database)):
    # 截取book参数 创建book对象(__dict__)返回book对象属性字典
    book_obj = Book(**book.__dict__) # orm对象
    db.add(book_obj)
    await db.commit()
    return book
```
### 数据库操作更新
先查到再更改找不到直接报错就行
***核心*** ：查询get- 属性重新赋值-》commit 提交到数据库
```python
###### 数据库操作更新
class BookUpdate(BaseModel):
    bookname: str
    author: str
    price: str
    publisher: str
@book.put("/book/update_book/{book_id}", summary="更新书籍", description="通过主键id先查询到然后重新赋值")
async def update_book(book_id:int, data:BookUpdate, db: AsyncSession = Depends(get_database)):
    #1.查询
    book = await db.get(Book, book_id)
    #判断是否存在
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    #2.修改属性
    book.bookname = data.bookname
    book.author = data.author
    book.price = data.price
    #3.提交
    await db.commit()
    return book
```
+ update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
```python
@book.put("/{book_id}", summary="更新书籍（部分更新）")
async def update_book(
    book_id: int,
    data: BookUpdate,
    db: AsyncSession = Depends(get_database)
):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)
    return book
```
+ update(Book).where(Book.id == book_id).values(**data.model_dump(exclude_unset=True))
```python
async def update_book(book_id: int, data: BookUpdate, db: AsyncSession):
    stmt = update(Book).where(Book.id == book_id).values(**data.model_dump(exclude_unset=True))
    await db.execute(stmt)
    await db.commit()
    # 注意：这样不会返回更新后的对象，你需要再次查询
    updated_book = await db.get(Book, book_id)
    return updated_book
```

###### 数据库操作删除
***核心*** 查询get--- delete 删除---- 提交到数据库
```python
@book.delete("/book/delete_book/{book_id}")
async def delete_book(book_id:int, db: AsyncSession = Depends(get_database)):
    # 先查询
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await db.delete(book)
    await db.commit()
    return {
        "msg": "删除成功"
    }
```