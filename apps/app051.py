# 文件上传 请求头Content-type：form-data
#
from typing import List

from fastapi import APIRouter, File, UploadFile

app051 = APIRouter()

# bytes表示字节流
@app051.post("/file")
async def get_file(file: bytes = File()):
    # 适合小文件
    print("hello world")
    print(file)
    return {
        "hi": "1"
    }

# 多个文件
@app051.post("/files")
async def get_files(files: List[bytes] = File()):
    # 适合小文件
    print("hello world")
    print(files)
    for file in files:
        print(len(file))
    return {
        'file': len(files)
    }
# 用的最多的
@app051.post("/uploadfile")
async def get_uploadfile(file: UploadFile):
    # 最常用的
    print("file", file)
    return {
        'file': file.filename
    }

@app051.post("/uploadfiles")
async def get_uploadfiles(files: List[UploadFile]):
    # 最常用的
    for file in files:
        print('file', file)
    return {
        'file': len(files)
    }