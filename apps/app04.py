from typing import Annotated, Optional, Union

from fastapi import Query, APIRouter

app04 = APIRouter()

@app04.get("/items/")
async def read_items(q: Annotated[Optional[str], Query(max_length=2)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## 更多的校验
# q: Annotated[str | None, Query(min_length=3, max_length=50)] = None
## 正则校验
# q: Annotated[ str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")] = None,

@app04.get("/items/")
async def read_items(q: Annotated[Union[list[str]] ,None, Query()] = None):
    query_items = {"q": q}
    return query_items

## http://localhost:8000/items/?q=foo&q=bar

## 你还可以定义在没有给定值时的默认 list：
@app04.get("/items/")
async def read_items(q: Annotated[list[str], Query()] = ["foo", "bar"]):
    query_items = {"q": q}
    return query_items
