from typing import Optional, Union

from fastapi import APIRouter
app02 = APIRouter()

# /work?id=1&name=xxx
# 注： 在查询函数 get_work中 声明不是路径参数, 就是查询参数
@app02.get("/work")
async def get_work(name: Optional[str] = None, id:int = 1):
    return {
        "msg": f'msg{id}-{name}'
    }

@app02.get("/items/{item_id}")
async def ref_item(item_id, q: Optional[str] = None):
    return {'item_id': item_id, "q": q}

@app02.get("/work/{gz}")
async def get_work(gz, name: Optional[str] = None, id:int = 1, ):
    return {
        "msg": f'msg{id}-{name}-{gz}'
    }

# Union[str, None] 表示即可以是str也可以是 None
# name: Union[str, None] = None 默认是None
# Optional[str] = Union[str, None] = None, 表示既可以是str也可以是none 默认是none
@app02.get("/work1/{gz}")
async def get_work(gz, name: Optional[str] = None, id:Union[str, int] = "1"):
    return {
        "msg": f'msg{id}-{name}-{gz}'
    }