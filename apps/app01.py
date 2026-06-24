from fastapi import APIRouter
app01 = APIRouter()

# /user/id  /user/1 /user/2
@app01.get("/user/{user_id}")

async def get_user(user_id): # 默认是str类型
    return {
        "user_id": user_id
    }

# /article/id /article/1 /article/2
@app01.get("/article/{id}")
async def get_user(id: int): ### 可以用int 指定int类型
    return {
        "article_id": id
    }