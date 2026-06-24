from fastapi import Request, APIRouter

app061 = APIRouter()

@app061.post("/items")
async def items(request: Request):
    # Request 表示 request参数已经是个request对象
    print('request', request)
    return {
        'request': 1
    }