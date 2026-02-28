import sys
import os
import logging

# 确保当前目录在 sys.path 中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from rag_service import rag_service
from database import db_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

knowledge_data = [
    {
        "title": "如何缓解考前焦虑",
        "content": "考前焦虑是大学生常见的心理问题。缓解方法包括：1. 制定合理的复习计划，避免临阵磨枪；2. 保持规律作息，保证充足睡眠；3. 进行深呼吸或冥想练习，放松身心；4. 适当运动，释放压力；5. 调整心态，接受适度焦虑有助于发挥，但不要过度担忧结果。"
    },
    {
        "title": "人际交往中的倾听技巧",
        "content": "有效倾听是建立良好人际关系的关键。技巧包括：1. 保持眼神接触，展示关注；2. 不打断对方，耐心听完；3. 适时给予回应，如点头或简单的“嗯”、“是的”；4. 尝试复述对方的观点，确认理解是否正确；5. 关注对方的情绪，而不仅仅是语言内容。"
    },
    {
        "title": "失眠的自我调节",
        "content": "改善失眠的建议：1. 建立固定的睡眠时间表；2. 睡前避免使用电子产品，减少蓝光刺激；3. 营造舒适的睡眠环境（黑暗、安静、适宜温度）；4. 避免下午摄入咖啡因；5. 睡前进行放松活动，如阅读、热水澡或轻柔拉伸。"
    },
    {
        "title": "应对抑郁情绪",
        "content": "如果你感到持续的低落，可以尝试：1. 接纳自己的情绪，不要自责；2. 保持规律的生活节奏；3. 坚持适量运动，促进多巴胺分泌；4. 与信任的朋友或家人倾诉；5. 设定小目标，逐步完成，建立成就感。注意：如果症状严重或持续时间长，请务必寻求专业心理医生的帮助。"
    }
]

def init_knowledge():
    # 初始化数据库连接
    db_manager.init_db()
    
    rag_available = True
    if rag_service.vector_store is None:
        logger.warning("⚠️ RAG服务未初始化，知识库将仅写入 MySQL，无法进行向量检索")
        rag_available = False

    logger.info("开始初始化公共知识库...")
    for item in knowledge_data:
        # 1. 尝试添加到向量数据库 (RAG)
        rag_success = False
        if rag_available:
            rag_success = rag_service.add_knowledge(
                uuid="public", # 公共知识
                title=item["title"],
                content=item["content"],
                k_type="public"
            )
            if not rag_success:
                 logger.warning(f"❌ RAG添加失败: {item['title']}")
        
        # 2. 无论 RAG 是否成功，都添加到 MySQL (用于列表展示)
        try:
            # 检查是否存在
            sql_check = "SELECT id FROM knowledge_base WHERE title = %s AND type = 'public'"
            res = db_manager.execute_query(sql_check, (item["title"],))
            
            if not res:
                sql_insert = "INSERT INTO knowledge_base (type, uuid, title, content, created_at) VALUES ('public', 'public', %s, %s, NOW())"
                db_manager.execute_update(sql_insert, (item["title"], item["content"]))
                status_msg = "MySQL ✅"
                if rag_available and rag_success:
                    status_msg += ", RAG ✅"
                elif rag_available and not rag_success:
                    status_msg += ", RAG ❌"
                else:
                    status_msg += ", RAG ⚠️ (不可用)"
                
                logger.info(f"已添加: {item['title']} [{status_msg}]")
            else:
                logger.info(f"⚠️ 已存在于数据库: {item['title']}")
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            
    logger.info("知识库初始化完成！")

if __name__ == "__main__":
    init_knowledge()
