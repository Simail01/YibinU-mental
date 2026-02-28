import logging
import json
import traceback
import uuid as uuid_module
from datetime import datetime
from database import db_manager
from rag_service import rag_service
from model_loader import model_loader

logger = logging.getLogger(__name__)

MAX_HISTORY_TURNS = 5
MAX_CONTEXT_LENGTH = 2048

class AnalysisService:
    def __init__(self):
        pass

    def deep_think(self, uuid, text, scl90_summary, knowledge_context):
        logger.info(f"[{uuid}] 开始深度思考")
        logger.info(f"[{uuid}] 步骤1: 分析用户意图 - 文本长度: {len(text)}")
        if scl90_summary:
            logger.info(f"[{uuid}] 步骤2: 关联SCL-90历史记录 - 已获取")
        else:
            logger.info(f"[{uuid}] 步骤2: 未找到SCL-90记录")
        if knowledge_context:
            logger.info(f"[{uuid}] 步骤3: 检索知识库 - 找到 {len(knowledge_context)} 条相关知识")
        return str(uuid)

    def _get_session_history(self, uuid, session_id):
        """获取会话历史，用于构建上下文"""
        if not session_id:
            return []
        
        sql = """
            SELECT user_query, system_reply, emotion, risk_level 
            FROM dialogue 
            WHERE uuid = %s AND session_id = %s 
            ORDER BY created_at ASC
            LIMIT %s
        """
        results = db_manager.execute_query(sql, (uuid, session_id, MAX_HISTORY_TURNS))
        return results or []

    def _build_conversation_context(self, history):
        """构建对话上下文字符串"""
        if not history:
            return ""
        
        context_parts = []
        for h in history[-MAX_HISTORY_TURNS:]:
            context_parts.append(f"用户：{h['user_query']}")
            context_parts.append(f"咨询师：{h['system_reply']}")
        
        context = "\n".join(context_parts)
        if len(context) > MAX_CONTEXT_LENGTH:
            context = context[-MAX_CONTEXT_LENGTH:]
        return context

    def _get_or_create_session(self, uuid, session_id=None):
        """获取或创建会话"""
        if session_id:
            sql = "SELECT session_id FROM dialogue_session WHERE session_id = %s AND uuid = %s"
            result = db_manager.execute_query(sql, (session_id, uuid))
            if result:
                return session_id
        
        new_session_id = str(uuid_module.uuid4())
        sql = "INSERT INTO dialogue_session (session_id, uuid, title, message_count) VALUES (%s, %s, %s, 0)"
        db_manager.execute_update(sql, (new_session_id, uuid, "新对话"))
        return new_session_id

    def _update_session(self, session_id, user_query):
        """更新会话信息"""
        title = user_query[:50] + "..." if len(user_query) > 50 else user_query
        sql = """
            UPDATE dialogue_session 
            SET message_count = message_count + 1, 
                title = CASE WHEN message_count = 0 THEN %s ELSE title END,
                updated_at = NOW()
            WHERE session_id = %s
        """
        db_manager.execute_update(sql, (title, session_id))

    def analyze(self, uuid, user_text, deep_thinking=False, session_id=None):
        """执行心理分析全流程，支持上下文记忆"""
        try:
            current_session_id = self._get_or_create_session(uuid, session_id)
            history = self._get_session_history(uuid, current_session_id)
            conversation_context = self._build_conversation_context(history)
            
            scl90_summary = ""
            sql = "SELECT total_score, abnormal_items FROM scl90_record WHERE uuid = %s ORDER BY created_at DESC LIMIT 1"
            scl_record = db_manager.execute_query(sql, (uuid,))
            if scl_record:
                rec = scl_record[0]
                abnormal = json.loads(rec['abnormal_items']) if isinstance(rec['abnormal_items'], str) else rec['abnormal_items']
                abnormal_str = "、".join([i['question'] for i in abnormal]) if abnormal else "无"
                scl90_summary = f"SCL-90总分: {rec['total_score']}, 异常症状: {abnormal_str}"

            knowledge_docs = rag_service.search(uuid, user_text)
            knowledge_context = "\n".join([doc.page_content for doc in knowledge_docs])
            
            if deep_thinking:
                self.deep_think(uuid, user_text, scl90_summary, knowledge_docs)
            
            emotion, risk = "未知", "未知"
            if model_loader.emotion_classifier:
                try:
                    emotion, risk = model_loader.emotion_classifier.discriminate(user_text)
                except Exception as e:
                    logger.error(f"情绪分析失败: {e}")
            
            advice = "系统维护中，无法生成建议。"
            if model_loader.advice_generator:
                try:
                    advice = model_loader.advice_generator.generate(
                        user_text=user_text, 
                        emotion=emotion, 
                        risk=risk, 
                        scl90_summary=scl90_summary,
                        rag_context=knowledge_context,
                        deep_thinking=deep_thinking,
                        conversation_history=conversation_context
                    )
                except Exception as e:
                    logger.error(f"建议生成失败: {e}")
                    advice = "抱歉，AI咨询师暂时无法回应，请稍后再试。"
            
            sql = """
                INSERT INTO dialogue (uuid, session_id, user_query, system_reply, emotion, risk_level, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            db_manager.execute_update(sql, (uuid, current_session_id, user_text, advice, emotion, risk))
            
            self._update_session(current_session_id, user_text)
            
            return {
                "code": 200,
                "msg": "分析成功",
                "data": {
                    "original_text": user_text,
                    "emotion": emotion,
                    "risk": risk,
                    "advice": advice,
                    "context_used": len(knowledge_docs) > 0,
                    "deep_thinking": deep_thinking,
                    "session_id": current_session_id
                }
            }
        
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(error_detail)
            return {
                "code": 500,
                "msg": f"服务器内部错误：{str(e)}",
                "data": None
            }

    def get_sessions(self, uuid):
        """获取用户的所有会话列表"""
        sql = """
            SELECT session_id, title, message_count, created_at, updated_at 
            FROM dialogue_session 
            WHERE uuid = %s 
            ORDER BY updated_at DESC
        """
        results = db_manager.execute_query(sql, (uuid,))
        
        if results:
            for r in results:
                if isinstance(r['created_at'], datetime):
                    r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(r['updated_at'], datetime):
                    r['updated_at'] = r['updated_at'].strftime("%Y-%m-%d %H:%M:%S")
        
        return {"code": 200, "data": results or []}

    def get_session_messages(self, uuid, session_id):
        """获取会话的所有消息"""
        sql = """
            SELECT id, user_query, system_reply, emotion, risk_level, created_at 
            FROM dialogue 
            WHERE uuid = %s AND session_id = %s 
            ORDER BY created_at ASC
        """
        results = db_manager.execute_query(sql, (uuid, session_id))
        
        if results:
            for r in results:
                if isinstance(r['created_at'], datetime):
                    r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        
        return {"code": 200, "data": results or []}

    def create_new_session(self, uuid):
        """创建新会话"""
        new_session_id = str(uuid_module.uuid4())
        sql = "INSERT INTO dialogue_session (session_id, uuid, title, message_count) VALUES (%s, %s, %s, 0)"
        db_manager.execute_update(sql, (new_session_id, uuid, "新对话"))
        return {"code": 200, "data": {"session_id": new_session_id}}

    def delete_session(self, uuid, session_id):
        """删除会话及其所有消息"""
        sql1 = "DELETE FROM dialogue WHERE uuid = %s AND session_id = %s"
        db_manager.execute_update(sql1, (uuid, session_id))
        
        sql2 = "DELETE FROM dialogue_session WHERE uuid = %s AND session_id = %s"
        db_manager.execute_update(sql2, (uuid, session_id))
        
        return {"code": 200, "msg": "会话已删除"}

analysis_service = AnalysisService()
