from database import db_manager

def migrate():
    print("开始数据库迁移...")
    
    # Check if columns exist or just try to add them (ignoring errors if they exist is messy in raw SQL without stored procedures)
    # But since it's dev, I'll just try to add them one by one.
    
    sqls = [
        "ALTER TABLE scl90_record ADD COLUMN average_score FLOAT DEFAULT 0",
        "ALTER TABLE scl90_record ADD COLUMN positive_items_count INT DEFAULT 0",
        "ALTER TABLE scl90_record ADD COLUMN answers JSON COMMENT '原始答案'"
    ]
    
    for sql in sqls:
        try:
            db_manager.execute_update(sql)
            print(f"执行成功: {sql}")
        except Exception as e:
            print(f"执行可能已跳过 (如列已存在): {e}")

    print("数据库迁移完成")

if __name__ == "__main__":
    migrate()
