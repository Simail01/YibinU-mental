import json
import logging
from datetime import datetime
from database import db_manager
from rag_service import rag_service
from scl90_logic import calculate_scl90_score

logger = logging.getLogger(__name__)

class SCL90Service:
    def submit_result(self, uuid, answers):
        """提交SCL-90测试结果"""
        try:
            # 计算得分 (包含验证逻辑)
            result = calculate_scl90_score(answers)
            
            # 保存到数据库
            sql = """
            INSERT INTO scl90_record (uuid, scores, total_score, abnormal_items, average_score, positive_items_count, answers)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db_manager.execute_update(sql, (
                uuid, 
                json.dumps(result['factor_results']), 
                result['total_score'], 
                json.dumps(result['abnormal_items']),
                result.get('average_score', 0),
                result.get('positive_items_count', 0),
                json.dumps(answers)
            ))
            
            # 同步到RAG
            summary = f"总分{result['total_score']}，"
            if result['abnormal_items']:
                summary += "异常项：" + "、".join([f"{item['question']}({item['score']}分)" for item in result['abnormal_items']])
            else:
                summary += "无明显异常项。"
                
            rag_service.sync_scl90_result(uuid, summary)
            
            return {
                "code": 200,
                "msg": "提交成功",
                "data": result
            }
        except ValueError as ve:
            return {"code": 400, "msg": str(ve)}
        except Exception as e:
            logger.error(f"提交失败: {e}")
            return {"code": 500, "msg": f"提交失败: {str(e)}"}

    def get_history(self, uuid):
        """获取SCL-90历史记录"""
        sql = "SELECT id, total_score, average_score, created_at FROM scl90_record WHERE uuid = %s ORDER BY created_at DESC"
        results = db_manager.execute_query(sql, (uuid,))
        
        # 格式化时间
        if results:
            for r in results:
                if isinstance(r['created_at'], datetime):
                    r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                # 兼容旧数据
                if r.get('average_score') is None or r.get('average_score') == 0:
                    r['average_score'] = round(r['total_score'] / 90.0, 2)
                
        return results or []

    def get_detail(self, uuid, record_id):
        """获取单次SCL-90详细记录"""
        sql = "SELECT * FROM scl90_record WHERE id=%s AND uuid=%s"
        results = db_manager.execute_query(sql, (record_id, uuid))
        
        if not results:
            return None
            
        record = results[0]
        
        # 构造前端 showResults 需要的数据结构
        factor_results = {}
        abnormal_items = []
        try:
            if record['scores']:
                factor_results = json.loads(record['scores']) if isinstance(record['scores'], str) else record['scores']
            if record['abnormal_items']:
                abnormal_items = json.loads(record['abnormal_items']) if isinstance(record['abnormal_items'], str) else record['abnormal_items']
        except Exception as e:
            logger.error(f"解析记录详情失败: {e}")

        # 兼容旧数据
        avg_score = record.get('average_score')
        if avg_score is None or avg_score == 0:
            avg_score = round(record['total_score'] / 90.0, 2)
            
        data = {
            "total_score": record['total_score'],
            "average_score": avg_score,
            "positive_items_count": record.get('positive_items_count', 0),
            "factor_results": factor_results,
            "abnormal_items": abnormal_items,
            "created_at": record['created_at'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(record['created_at'], datetime) else str(record['created_at'])
        }
        
        return data

scl90_service = SCL90Service()
