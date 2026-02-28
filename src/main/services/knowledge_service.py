import logging
from datetime import datetime
from database import db_manager
from rag_service import rag_service

logger = logging.getLogger(__name__)

class KnowledgeService:
    def add_knowledge(self, uuid, title, content):
        """添加个人知识库"""
        success = rag_service.add_knowledge(uuid, title, content, k_type="private")
        if success:
            # 同时存入MySQL方便列表展示
            sql = "INSERT INTO knowledge_base (type, uuid, title, content) VALUES ('private', %s, %s, %s)"
            db_manager.execute_update(sql, (uuid, title, content))
            return {"code": 200, "msg": "添加成功", "data": None}
        else:
            return {"code": 500, "msg": "添加失败"}

    def list_knowledge(self, uuid):
        """列出知识库（公共+个人）"""
        sql = "SELECT id, title, content, type, created_at FROM knowledge_base WHERE type='public' OR (type='private' AND uuid=%s) ORDER BY created_at DESC"
        results = db_manager.execute_query(sql, (uuid,))
        
        # 格式化
        if results:
            for r in results:
                 if isinstance(r['created_at'], datetime):
                    r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M")
                    
        return results or []

    def delete_knowledge(self, uuid, knowledge_id):
        """删除知识库条目"""
        # 只能删除自己的私有知识
        sql = "DELETE FROM knowledge_base WHERE id=%s AND uuid=%s AND type='private'"
        affected = db_manager.execute_update(sql, (knowledge_id, uuid))
        if affected and affected > 0:
            return {"code": 200, "msg": "删除成功"}
        else:
            return {"code": 404, "msg": "删除失败：未找到记录或无权操作"}

    def get_knowledge_detail(self, uuid, knowledge_id):
        """获取知识详情"""
        sql = "SELECT id, title, content, type, uuid, created_at FROM knowledge_base WHERE id=%s"
        results = db_manager.execute_query(sql, (knowledge_id,))
        if results:
            item = results[0]
            # 权限检查：如果是私有且不属于该用户
            if item['type'] == 'private' and item.get('uuid') != uuid:
                 return {"code": 403, "msg": "无权访问"}
            
            if isinstance(item['created_at'], datetime):
                item['created_at'] = item['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            return {"code": 200, "data": item}
        return {"code": 404, "msg": "未找到记录"}

    def search_knowledge(self, uuid, query):
        """搜索知识库"""
        docs = rag_service.search(query, uuid)
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "title": doc.metadata.get("title", ""),
                "type": doc.metadata.get("type", "private")
            })
        return {"code": 200, "data": results}

knowledge_service = KnowledgeService()
