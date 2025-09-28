from pymongo import MongoClient
import json
import os
from datetime import datetime
from tqdm import tqdm


def export_database_with_progress():
    # 连接配置
    MONGODB_URI = "mongodb://localhost:27017"
    DATABASE_NAME = "web"

    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    # 创建备份目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"{DATABASE_NAME}_backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)

    print(f"📦 开始导出数据库: {DATABASE_NAME}")
    print("=" * 60)

    # 获取集合信息
    collections = []
    for coll_name in db.list_collection_names():
        coll = db[coll_name]
        count = coll.count_documents({})
        collections.append({
            'name': coll_name,
            'count': count,
            'collection': coll
        })

    # 按文档数量排序（从大到小）
    collections.sort(key=lambda x: x['count'], reverse=True)

    total_docs = sum(coll['count'] for coll in collections)
    print(f"📊 总共 {len(collections)} 个集合, {total_docs} 个文档")

    # 导出每个集合
    for coll_info in collections:
        if coll_info['count'] == 0:
            print(f"⏭️  跳过空集合: {coll_info['name']}")
            continue

        output_file = os.path.join(backup_dir, f"{coll_info['name']}.json")
        print(f"📁 导出: {coll_info['name']} ({coll_info['count']} 文档)")

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                exported = 0

                # 使用进度条
                for doc in tqdm(coll_info['collection'].find(),
                                total=coll_info['count'],
                                desc=f"  {coll_info['name']}"):
                    # 处理特殊类型
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])

                    json.dump(doc, f, ensure_ascii=False, default=str)
                    f.write('\n')
                    exported += 1

            print(f"  ✅ 成功导出 {exported} 个文档")

        except Exception as e:
            print(f"  ❌ 导出失败: {e}")

    print("=" * 60)
    print(f"🎉 数据库导出完成!")
    print(f"📍 备份位置: {os.path.abspath(backup_dir)}")

    client.close()


if __name__ == "__main__":
    export_database_with_progress()