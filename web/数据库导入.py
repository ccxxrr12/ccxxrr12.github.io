from pymongo import MongoClient
import json
import os
from datetime import datetime
from tqdm import tqdm
import glob


def import_database_with_progress(backup_dir=None):
    # 连接配置
    MONGODB_URI = "mongodb://localhost:27017"
    DATABASE_NAME = "web"

    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    # 如果没有指定备份目录，查找最新的备份
    if backup_dir is None:
        backup_dirs = glob.glob(f"{DATABASE_NAME}_backup_*")
        if not backup_dirs:
            print("❌ 没有找到备份目录")
            return
        # 按创建时间排序，选择最新的
        backup_dirs.sort(key=lambda x: os.path.getctime(x), reverse=True)
        backup_dir = backup_dirs[0]

    print(f"📦 开始导入数据库: {DATABASE_NAME}")
    print(f"📍 从目录导入: {backup_dir}")
    print("=" * 60)

    # 获取所有JSON文件
    json_files = glob.glob(os.path.join(backup_dir, "*.json"))
    if not json_files:
        print("❌ 备份目录中没有找到JSON文件")
        return

    total_files = len(json_files)
    print(f"📊 找到 {total_files} 个集合文件")

    # 导入每个集合
    for file_path in json_files:
        coll_name = os.path.basename(file_path).replace('.json', '')
        print(f"📁 导入集合: {coll_name}")

        # 读取JSON文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = []
                for line in f:
                    if line.strip():
                        documents.append(json.loads(line))
        except Exception as e:
            print(f"  ❌ 读取文件失败: {e}")
            continue

        if not documents:
            print(f"  ⏭️  跳过空文件: {coll_name}")
            continue

        print(f"  📊 找到 {len(documents)} 个文档")

        # 获取集合引用
        collection = db[coll_name]

        # 检查集合是否已存在文档
        existing_count = collection.count_documents({})
        if existing_count > 0:
            print(f"  🔄 集合已存在 ({existing_count} 个文档)，将整合数据...")

        # 导入文档
        try:
            inserted_count = 0
            updated_count = 0

            # 使用进度条
            for doc in tqdm(documents, desc=f"  导入 {coll_name}"):
                # 处理_id字段
                if '_id' in doc:
                    # 检查是否已存在相同_id的文档
                    existing_doc = collection.find_one({'_id': doc['_id']})
                    if existing_doc:
                        # 更新现有文档
                        collection.replace_one({'_id': doc['_id']}, doc)
                        updated_count += 1
                    else:
                        # 插入新文档
                        collection.insert_one(doc)
                        inserted_count += 1
                else:
                    # 没有_id字段，直接插入
                    collection.insert_one(doc)
                    inserted_count += 1

            print(f"  ✅ 成功导入: {inserted_count} 新增, {updated_count} 更新")

        except Exception as e:
            print(f"  ❌ 导入失败: {e}")

    print("=" * 60)
    print(f"🎉 数据库导入完成!")

    # 显示导入后的统计信息
    print("\n📊 数据库当前状态:")
    for coll_name in db.list_collection_names():
        count = db[coll_name].count_documents({})
        print(f"  {coll_name}: {count} 个文档")

    client.close()


if __name__ == "__main__":
    # 可以指定备份目录，如果不指定则使用最新的备份
    import_database_with_progress()
    # 或者指定特定目录: import_database_with_progress("web_backup_20231201_123456")