import motor.motor_asyncio#modgodb数据库异步库
from datetime import datetime, date#时间函数库
from typing import Dict, List, Any #数据类型库
import os
import pathlib
import asyncio  #异步库
from bson import ObjectId#转化文档id的函数，将字符串转化为id

#文件断点下载，记录断点位置
async def add_file_uploads(name:str,num:int,total:int):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    
    result = await collection.update_one(
        {"filename": name},
        {
            "$addToSet": {"value": num},  # 直接存储数字，MongoDB会转为数组元素
            "$setOnInsert": {
                "filename": name,
                "total_chunks": total,
                "created_at": datetime.combine(date.today(), datetime.min.time()),
            }
        },
        upsert=True
    )
    client.close()
    return result
#文件断点下载，返回记录断点位置
async def find_file_uploads(name:str,total:int):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['file_uploads']

    result = await collection.find_one(
        {"filename": name,"total_chunks":total},
        {"filename":1,"value":1,"_id":0
        },
    )

    client.close()
    return result

#关键字记录函数
async def add_key(key: str, id, name: str, scribe: str):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['search-note']

    zidian = {
        "name": name,#关键字对应的文档名字
        "scribe": scribe,#文档的粗描述
        "date": datetime.combine(date.today(), datetime.min.time()),#创建日期
    }

    # 使用upsert：如果文档不存在则创建，存在则更新
    result = await collection.update_one(
        {"key": key},
        {
            "$set": {f"word-id.{id}": zidian},
            "$setOnInsert": {"key": key}  # 只在插入时设置key字段
        },
        upsert=True  # 启用upsert选项，没有则创建
    )
    client.close()

#笔记保存
#文档格式：
# #笔记：设置一个数据库集合（note），来保存笔记
#_id：自动生成即可
#name：笔记名字
#contect-key：笔记内关键字
#key：笔记关键字
#context：字典，笔记内关键字：笔记内容（字典格式，组织成表格形式）{列：行内容}
#scribe：笔记和笔记名在一起的笔记内介绍，更加详细
#directory：上级目录名字
#annotation：字典，笔记内关键字：[批注id列表]
async def add_note(name: str, contectkey: list,  context: Dict, scribe: str,int_directory:str,se_directory:str,top_directory:str,id:str=None):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['note']


    # 构建完整的笔记文档
    note_document = {
        "name": name,
        "contect-key": contectkey,
        "content": context,  # 表格形式的字典，字典，键为关键字，值为列表，列表为每一行
        "scribe": scribe,
        "directory": {"directory":int_directory,"sedirectory":se_directory,"topdirectory": top_directory},
        "int-directory": int_directory,
        "se-directory": se_directory,  # 二级目录，用于返回上级目录
        "top-directory": top_directory,#二级目录，用于返回上级目录
        "created_at": datetime.combine(date.today(), datetime.min.time()),  # 添加创建时间
    }

    if id is None:
        result = await collection.insert_one(note_document)
    else:
        result = await collection.replace_one({"_id": ObjectId(id)},note_document)

    client.close()

#文章：
#设置一个数据库集合（article），来保存文章
#每个文章构成一个文档
#文档格式：
#_id：自动生成即可
#name：文章名字
#key：文章关键字
#context：文章内容
#image：字典{image1：地址}
#scribe：文章内介绍，详细
#directory：上级目录名字
async def add_article(
        name: str,
        key: str,
        context: str,
        image: Dict[str, str] = None,
        scribe: str = "",
        directory: str = "默认目录",
        tags: List[str] = None,
) :

    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['article']


    # 构建文章文档
    article_document = {
        "name": name.strip(),
        "key": key.strip(),
        "context": context,#文字内容
        "image": image or {},
        "scribe": scribe.strip(),
        "directory": directory.strip(),
        "tags": tags or [],
        "date": datetime.combine(date.today(), datetime.min.time()),
    }
    result = await collection.insert_one(article_document)
    client.close()


#设置集合（directory）来保存资源结构
#文档格式：
#_id：自动生成即可
#name：目录名字
#class：目录级别（大小细分别为123）
#directory：上级目录名字（用于构建结构关系，查询该字段形成内外映射：上级目录映射下级目录）
#scribe:目录介绍，详细
#触发器1—下一级创建目录或者删除，更新next内容
#查询文档-文章
async def add_directory(
        name: str,
        class_level: int,
        parent_directory: str = "根目录",
        scribe: str = ""
) :
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['directory']

    # 构建目录文档
    directory_document = {
        "name": name.strip(),
        "class": class_level,
        "directory": parent_directory.strip(),
        "scribe": scribe.strip()
    }

    result = await collection.insert_one(directory_document)
    client.close()

#批注是单独小文本模块，为后续为文章和笔记的补充
#设置集合（annotation_note、annotation_article）保存
#Note文档格式：
#_id：自动生成即可
#main_text_id：保存批注的笔记id
#main_key：保存批注对应笔记内关键字
#contect：批注内容
async def add_note_annotation(
        main_text_id: str,
        main_key: str,
        content: str
):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['annotation_note']
    # 构建批注文档
    annotation_document = {
        "main_text_id": main_text_id.strip(),
        "main_key": main_key.strip(),
    }
    result = await collection.update_one({"main_text_id": main_text_id,"main_key": main_key},
    {
        "$set": {"content": content},
        "$setOnInsert": annotation_document  # 只在插入时创建全新数据
    },
    upsert = True  # 启用upsert选项，没有则创建
                                         )
    client.close()

#取批注
async def find_note_annotation(main_text_id:str,main_key:str):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['annotation_note']
    result = await collection.find_one({"main_text_id": main_text_id,"main_key": main_key})
    return result






#文档格式
#_id：自动生成即可
#file-name：文件名
#data-type：文件类型分类
#extension：文件扩展名
#size：文件大小
#ico：文件图标
#date：创建日期
#path：文件路径
async def add_file(
        filename: str
):
    abspath="D:/python_programe/数据库开发/web笔记系统/file/"+filename
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['file']

    filename_object = pathlib.Path(filename)
    extension = filename_object.suffix.lower()
    filename_name = filename_object.stem
    data_type=""
    if extension in ['.doc', '.docx', '.pdf', '.txt', '.xls', '.xlsx','.py','.cpp']:
        data_type = 'document'
    elif extension in ['.jpg', '.jpeg', '.png', '.gif']:
        data_type = 'image'
    elif extension in [".exe"]:
        data_type = 'executable'
    elif extension in [".zip",".tar",".rar"]:
        data_type = 'archive'

    a={'.pdf': 'fa-file-pdf',
    '.doc': 'fa-file-word',
    '.cpp': 'fa-file-cpp',
    '.docx': 'fa-file-word',
    '.xls': 'fa-file-excel',
    '.py': 'fa-file-python',
    '.xlsx': 'fa-file-excel',
    '.jpg': 'fa-file-image',
    '.jpeg': 'fa-file-image',
    '.png': 'fa-file-image',
    '.gif': 'fa-file-image',
    '.mp4': 'fa-file-video',
    '.avi': 'fa-file-video',
    '.mov': 'fa-file-video',
    '.mp3': 'fa-file-audio',
    '.wav': 'fa-file-audio',
    '.zip': 'fa-file-archive',
    '.rar': 'fa-file-archive',
    '.tar': 'fa-file-archive',
    '.txt': 'fa-file-alt',
    '.exe': 'fa-cog'}

    stat=os.stat(abspath)
    size=stat.st_size
    size=round(size/(1024*1024),2)
    # 构建批注文档
    annotation_document = {
        "file-name": filename_name,
        "data-type": data_type,
        "extension": "file-icon "+extension[1:],
        "size": str(size)+"MB",
        "date": datetime.combine(date.today(), datetime.min.time()),
        "path": "file/"+filename,
        "icon": "fas "+a[extension],
    }
    result = await collection.insert_one(annotation_document)
    client.close()


####以下是查询函数

#取笔记，由id取
async def find_note(id:any=None):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['note']
    if id:
        cursor = collection.find({"_id":id})
    else:
        cursor = collection.find({})
    documents = []
    async for document in cursor:
        documents.append(document)
    client.close()
    return documents

#取文章，由id取
async def find_article(id:any=None):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['article']
    if id:
        cursor = collection.find({"_id": id})
    else:
        cursor = collection.find({})
    documents = []
    async for document in cursor:
        documents.append(document)
    client.close()
    return documents

#取文件，所有
async def find_file():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['file']
    cursor = collection.find({})
    documents = []
    async for document in cursor:
        documents.append(document)
    client.close()
    return documents

#取目录，由class级别123取
async def find_directory(level:int,parent_directory:any=None):
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['web']
    collection = db['directory']
    if parent_directory:
        cursor = collection.find({"class": level, "directory": parent_directory},{"_id": 0,"name":1,"class":1,"directory":1,"scribe":1})
        documents = []
        async for document in cursor:
            documents.append(document)
        client.close()
        return documents
    else:
        cursor = collection.find({"class":level},{"_id": 0,"name":1,"class":1,"directory":1,"scribe":1})
        documents = []
        async for document in cursor:
            documents.append(document)
        client.close()
        return documents

    #asyncio.run(add_note("第三篇示例", [1,2,3], ["q丁诚","w第三方测试"], {"1":"一","2":"二","3":"三"}, "测试文档第三篇","默认", ))
'''c=asyncio.run(find_note(ObjectId("68b15b9adff17db4e7b356b7")))
print(c[0])'''

