from email.policy import default
from operator import gt

from fastapi import APIRouter
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

class Item(BaseModel):

    name: str = Field(reg='^a') # 正则表示 小写a开头
    description: Optional[str] = None
    price: float
    friends: List[int]
    birth: date # 日期
    ids: int = Field(default=1, gt = 0, lt = 100)
    tax: Optional[float] = None # float 或者 none 默认none

app03 = APIRouter()

# /user/id  /user/1 /user/2
@app03.post("/user")
async def get_jobs(data: Item ):
    # data.id = user_id
    # print(user_id)
    item_dict = data.dict()  # 关键：转换为字典

    return {
        # "id33": user_id,
        **item_dict,
        "a": "heloo"
    }

@app03.post("/uer1/{user_id}")
async def get_jobs(data: Item , user_id: int):
    # data.id = user_id
    print(user_id)
    item_dict = data.dict()  # 关键：转换为字典

    return {
        # "id33": user_id,
        **item_dict,
        "a": "heloo",
        "a_id": user_id
    }
