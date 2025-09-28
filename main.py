import datetime
from typing import Optional
import shutil
from fastapi import FastAPI, Request, HTTPException, UploadFile, File,Form
from fastapi.responses import HTMLResponse,JSONResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import json
from setuptools.command.build_ext import if_dl

from db_deal import *
import os
from fastapi.responses import FileResponse
# 创建一个app实例
app = FastAPI(title="MyWeb-note", version="1.0.0")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="templates")

# Request包含http请求的所有信息，需要使用，q 是一个查询参数（Query Parameter），是URL中 ? 后面的参数。

'''这是目录系统，三级目录划分'''
@app.get("/", response_class=HTMLResponse)
async def read(request:Request,num:int=1,mu:str=None):
    """num和mu是本级别目录，返回下一级所有目录信息，创建下一级目录页面"""
    if mu is None :
        mulu = await find_directory(num, mu)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "mulu": mulu}
        )
    elif num ==5:
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['web']
        collection = db['directory']
        print(mu)
        document =await collection.find_one({"name":mu,"class":2})

        if document:
            print(document)
        else:
            print("没有找到匹配的文档")
        mu=document["directory"]
        print(mu)
        mulu = await find_directory(2, mu)
        print(mulu)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "mulu": mulu}
        )

    else:
        num+=1
        if num<=3:
            mulu = await find_directory(num, mu)
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "mulu": mulu}
            )
        else:#打开笔记
            client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
            db = client['web']
            collection = db['note']
            cursor = collection.find({"int-directory":mu})
            documents = []
            async for document in cursor:
                documents.append(document)
            client.close()
            return templates.TemplateResponse(
                "directory_note.html",
                {"request": request, "mulu":documents }
            )


"""创建目录页面"""
@app.get("/create-directory", response_class=HTMLResponse)
async def create_directory(request:Request,mu:str=None):
    return templates.TemplateResponse(
        "createmulu.html",
        {"request": request}
    )



"""保存新建目录"""
@app.post("/create-directory")
async def create_directory( data: Dict[str, Any]):
    data["level"]=int(data["level"])
    c=await add_directory(data["name"],data["level"],data["directory"],data["description"])
    return { "消息": "内容已经接收"}






"""创建笔记阅读的界面"""
@app.get("/note")
async def read_note(request:Request,id:str):
    c = await find_note(ObjectId(id))
    d=c[0]
    return templates.TemplateResponse(
        "note.html",
        {"request": request, "note": d}
    )
"""修改笔记"""
@app.get("/updatanote")
async def update_note(request:Request,id:str):
    return templates.TemplateResponse(
        "updatanote.html",
        {"request": request}
    )


"""仅获取笔记内容"""
@app.get("/get-note")
async def get_note(id: str):
    try:
        # 验证ObjectId格式
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="无效的ID格式")

        # 获取笔记数据
        note_data = await find_note(ObjectId(id))

        # 检查是否找到笔记
        if not note_data:
            raise HTTPException(status_code=404, detail="笔记未找到")

        # 确保返回的是单个对象，不是数组
        # 如果你的 find_note 返回列表，取第一个元素
        if isinstance(note_data, list):
            if len(note_data) == 0:
                raise HTTPException(status_code=404, detail="笔记未找到")
            note_data = note_data[0]

        # 转换为可序列化的格式
        serializable_note = {
            "id": str(note_data.get("_id", "")),
            "name": note_data.get("name", ""),  # 注意：前端使用 name，不是 title
            "scribe": note_data.get("scribe", ""),  # 注意：前端使用 scribe，不是 description
            "keywords": note_data.get("contect-key", []),
            "content": note_data.get("content", {}),
            "directory": note_data.get("directory", ""),
            "sedirectory": note_data.get("se-directory", ""),
            "topdirectory": note_data.get("top-directory", ""),
            "intdirectory": note_data.get("int-directory", "")
        }

        return serializable_note

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取笔记内容错误: {str(e)}")



"""创建笔记note的页面"""
@app.get("/creat-note/{gn:str}")
async def creatnote(request:Request,gn:str):
    #开启编写文本页面，或者返回目录结构给编写文本页面
    if gn=="index":#打开网页
        html_file_path = "D:/python_programe/数据库开发/web笔记系统/templates/createnote.html"
        return FileResponse(html_file_path)
    elif gn=="mulu":#获取目录数据（嵌套字典格式）
        """{1-1：{2-1：[3-1]
                  2-2:[3-2] }        
            1-2: {2-1：[3-1]
                  2-2:[3-2] }     
            }"""
        m1=await find_directory(1)
        muludict = {}
        for i in m1:#i是1级目录
            m2=await find_directory(2,i["name"])
            dictmuli={}
            for j in m2:#j是二级目录
                m3=await find_directory(3,j["name"])
                listmuli=[]#三级目录列表
                for k in m3:
                    listmuli.append(k["name"])
                dictmuli.update({j["name"]: listmuli})
            muludict.update({i["name"]: dictmuli})
        return  muludict
    elif gn=="newmulu":#获取目录数据，用于创建目录
        """格式：
        {level1：一级目录，level2：二级目录，level3：三级目录}"""
        m1=await find_directory(1)

        m2=await find_directory(2)

        m3=await find_directory(3)

        data={"level1":m1,"level2":m2,"level3":m3}

        return data

"""从前端接收笔记内容，并保存到数据库中"""
@app.post("/putnote")
async def cmmint_date(data: Dict[str, Any]):
    c=data.keys()

    if "id" in c:
        await add_note(data["title"],data["keywords"],data["content"],data["description"],data["directory"],data["sedirectory"],data["topdirectory"],data["id"])
        return {"status": "成功访问", "消息": "内容已经接收"}
    else:
        await add_note(data["title"], data["keywords"], data["content"], data["description"], data["directory"],
                       data["sedirectory"], data["topdirectory"])
        return {"status": "成功访问", "消息": "内容已经接收"}

'''批注系统'''
"""读取或者保存"""
#获取批注内容
@app.get("/annotation")
async def get_annotation(note_id: str, key: str):
    try:
        result = await find_note_annotation(note_id, key)
        if result:
            return {"success": True, "annotation": result.get("content", "")}
        else:
            return {"success": True, "annotation": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取批注错误: {str(e)}")


# 保存批注 - POST请求
@app.post("/annotation")
async def save_annotation(data: Dict[str, Any]):
    try:
        note_id = data.get("note_id")
        key = data.get("key")
        annotation_content = data.get("annotation")

        if not all([note_id, key]):
            raise HTTPException(status_code=400, detail="缺少必要参数: note_id 或 key")

        result = await add_note_annotation(note_id, key, annotation_content)
        return {"success": True, "message": "批注保存成功", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存批注错误: {str(e)}")






"""文件传输系统"""
"""文件传输首页"""
@app.get("/files", response_class=HTMLResponse)
async def read_root(request: Request):
    file = await find_file()
    return templates.TemplateResponse(
        "fileshare.html",
        {"request": request,"filelist": file}
    )
"""由文件路径进行文件下载"""
@app.get("/file/{file_path:path}")
async def download_file(file_path: str):
    full_path = f"file/{file_path}"

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    if os.path.isdir(full_path):
        raise HTTPException(status_code=400, detail="detail不能下载目录 ")

    return FileResponse(
        path=full_path,
        filename=os.path.basename(file_path),  # 只保留文件名
        media_type='application/octet-stream'
    )

"""小型文件上传"""
@app.post("/uploads")
async def upload_file(file: UploadFile = File(...)):
    with open(f"file/{file.filename}", "wb") as buffer:
        chunk = await file.read()
        buffer.write(chunk)
    a=await add_file(file.filename)

""""#大型文件上传，分片上传"""
@app.post("/upload/chunk")
async def upload_chunk(
        file: UploadFile = File(...),
        filename: str = Form(...),  # 原始文件名
        chunk_index: int = Form(...),  # 分片序号（0开始）
        total_chunks: int = Form(...)  # 总分片数
):
    UPLOAD_DIR="D:/python_programe/数据库开发/web笔记系统/tempfile/"

    # 分片临时存储路径（用文件名+序号作为唯一标识）
    chunk_path = UPLOAD_DIR + f"{filename}.part{chunk_index}"

    # 写入分片（异步写入，减少IO阻塞）
    with open(chunk_path, "wb") as f:
        content = await file.read()
        f.write(content)
    c=await add_file_uploads(filename,chunk_index, total_chunks)
    return {"status": "chunk_received", "chunk_index": chunk_index}

'''大型文件合并'''
@app.post("/upload/merge")
async def upload_chunk(filename: str = Form(...),total_chunks: int = Form(...) ):
    filepath = "D:/python_programe/数据库开发/web笔记系统/file/"
    UPLOAD_DIR = "D:/python_programe/数据库开发/web笔记系统/tempfile/"
    target_path = filepath + filename
    with open(target_path, "wb") as target_file:
        for i in range(total_chunks):
            part_path = UPLOAD_DIR + f"{filename}.part{i}"
            with open(part_path, "rb") as part_file:
                target_file.write(part_file.read())
            #os.remove(part_path)  # 删除临时分片
        return {"status": "completed", "filename": filename}

'''用数据库支持断点传输'''
# key: filename, value: set of completed chunk indexes
@app.post("/upload/check")
async def check_upload(filename: str = Form(...), total_chunks: int = Form(...)):
    # 返回已上传的分片序号，前端可跳过这些分片
    c=await find_file_uploads(filename, total_chunks)
    uploaded_chunks=c[0]
    return {"completed_chunks": list(uploaded_chunks.get("value", set()))}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5418,
        reload=True,
        log_level="debug"
    )