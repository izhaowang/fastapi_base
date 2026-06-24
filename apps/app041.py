from fastapi import APIRouter, Form

app041 = APIRouter()
#  Form表单放置在请求体里面，请求头 Content-type： x-www-form-urlencoded
# 注册
@app041.post("/regin")
async def get_login(username: str = Form(), password: str= Form()):
    return {
        username: username,
        password: password
    }