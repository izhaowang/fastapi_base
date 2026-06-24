'''
orm操作 对数据进行增删改查
'''
from fastapi import HTTPException, status, Query
from typing import Optional, Union

from pydantic import BaseModel
from sqlalchemy import select, func
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import exclude

from orm.createa_async_engine import Book
from orm.create_depends import get_database
from fastapi import APIRouter
book = APIRouter()

@book.get("/book/books")
async def get_books_list(db: AsyncSession = Depends(get_database)):
    # 查询

    result = await db.execute(select(Book))
    book = result.scalars().all()
    return book
@book.get("/book/{book_id}")
async def get_book_byId(book_id: int, db: AsyncSession = Depends(get_database)):
    # stmt = select(Book).where(Book.id == book_id)
    # result = await db.execute(stmt)
    # book = result.scalar_one_or_none()
    # if book is None:
    #     raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    # return book
    book = await db.get(Book, book_id)
    return book

# 模糊查询作者以zhao开头
# % 是匹配任意个字符
# _ 是匹配单个字符
@book.get("/book/search_book/{authorName}")
async def get_search_book(authorName:str, db: AsyncSession = Depends(get_database)):
    content = select(Book).where(Book.author.like(f"{authorName}%"))
    content1 = select(Book).where(Book.author.like((f"{authorName}%")) & (Book.price >= 10))
    result = await db.execute(content)
    book = result.scalars().all()
    return book


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

###### 数据库操作新增
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

@book.put("/bool/update1/{book_id}", summary="更新书籍（部分更新）")
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
# class Person(BaseModel):
#     name: Optional[str] = None
#     age: Optional[str] = None
# def model_dump_test():
#     person = Person(name="zw1", age=10)
#     data = Person(name="zw2",age=18)
#     update_data = data.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(person, key, value)     # 字典直接赋值
#     print(person)
# model_dump_test()

###### 数据库操作删除
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