import traceback
import logging
from flask import Blueprint, request, jsonify

from scl90_logic import SCL90_QUESTIONS
from services.scl90_service import scl90_service
from utils.request_utils import get_uuid
from utils.validation import validate_json, validate_uuid, SCL90SubmitRequest

scl90_bp = Blueprint('scl90', __name__)
logger = logging.getLogger(__name__)


@scl90_bp.route("/questions", methods=["GET"])
def get_scl90_questions():
    return jsonify({
        "code": 200,
        "data": SCL90_QUESTIONS
    })


@scl90_bp.route("/submit", methods=["POST"])
@validate_uuid
@validate_json(SCL90SubmitRequest)
def submit_scl90():
    try:
        uuid = request.uuid
        validated = request.validated_data
        answers = validated.answers
        
        result = scl90_service.submit_result(uuid, answers)
        return jsonify(result)
        
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"code": 500, "msg": f"提交失败: {str(e)}"})


@scl90_bp.route("/history", methods=["GET"])
@validate_uuid
def get_scl90_history():
    uuid = request.uuid
    history = scl90_service.get_history(uuid)
    return jsonify({
        "code": 200,
        "data": history
    })


@scl90_bp.route("/detail/<int:record_id>", methods=["GET"])
@validate_uuid
def get_scl90_detail(record_id):
    uuid = request.uuid
    detail = scl90_service.get_detail(uuid, record_id)
    if not detail:
        return jsonify({"code": 404, "msg": "记录不存在"})
        
    return jsonify({
        "code": 200,
        "data": detail
    })
