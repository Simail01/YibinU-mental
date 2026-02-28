import traceback
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

from services.analysis_service import analysis_service
from database import db_manager
from utils.request_utils import get_uuid
from utils.validation import validate_json, validate_uuid, MentalAnalysisRequest

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)


class SessionRequest:
    pass


@analysis_bp.route("/mental_analysis", methods=["POST"])
@validate_uuid
@validate_json(MentalAnalysisRequest)
def mental_analysis_api():
    try:
        uuid = request.uuid
        validated = request.validated_data
        user_text = validated.text
        deep_thinking = validated.deep_thinking
        session_id = request.json.get('session_id', None)
        
        result = analysis_service.analyze(uuid, user_text, deep_thinking=deep_thinking, session_id=session_id)
        return jsonify(result)
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"code": 500, "msg": f"服务器内部错误：{str(e)}"})


@analysis_bp.route("/sessions", methods=["GET"])
@validate_uuid
def get_sessions():
    uuid = request.uuid
    result = analysis_service.get_sessions(uuid)
    return jsonify(result)


@analysis_bp.route("/sessions", methods=["POST"])
@validate_uuid
def create_session():
    uuid = request.uuid
    result = analysis_service.create_new_session(uuid)
    return jsonify(result)


@analysis_bp.route("/sessions/<session_id>", methods=["GET"])
@validate_uuid
def get_session_detail(session_id):
    uuid = request.uuid
    result = analysis_service.get_session_messages(uuid, session_id)
    return jsonify(result)


@analysis_bp.route("/sessions/<session_id>", methods=["DELETE"])
@validate_uuid
def delete_session_api(session_id):
    uuid = request.uuid
    result = analysis_service.delete_session(uuid, session_id)
    return jsonify(result)


@analysis_bp.route("/dialogue/history", methods=["GET"])
@validate_uuid
def get_dialogue_history():
    uuid = request.uuid
    
    sql = "SELECT id, user_query, system_reply, created_at FROM dialogue WHERE uuid=%s ORDER BY created_at ASC"
    results = db_manager.execute_query(sql, (uuid,))
    
    if results:
        for r in results:
             if isinstance(r['created_at'], datetime):
                r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            
    return jsonify({
        "code": 200,
        "data": results or []
    })


@analysis_bp.route("/dialogue/history", methods=["DELETE"])
@validate_uuid
def clear_dialogue_history():
    uuid = request.uuid
    
    sql = "DELETE FROM dialogue WHERE uuid=%s"
    db_manager.execute_update(sql, (uuid,))
    
    return jsonify({"code": 200, "msg": "历史记录已清空"})
