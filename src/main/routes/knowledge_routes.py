import logging
from flask import Blueprint, request, jsonify

from services.knowledge_service import knowledge_service
from utils.request_utils import get_uuid
from utils.validation import validate_json, validate_uuid, KnowledgeAddRequest

knowledge_bp = Blueprint('knowledge', __name__)
logger = logging.getLogger(__name__)


@knowledge_bp.route("/add", methods=["POST"])
@validate_uuid
@validate_json(KnowledgeAddRequest)
def add_knowledge():
    uuid = request.uuid
    validated = request.validated_data
    
    result = knowledge_service.add_knowledge(
        uuid, 
        validated.title, 
        validated.content
    )
    return jsonify(result)


@knowledge_bp.route("/list", methods=["GET"])
@validate_uuid
def list_knowledge():
    uuid = request.uuid
    
    knowledge_list = knowledge_service.list_knowledge(uuid)
    return jsonify({
        "code": 200,
        "data": knowledge_list
    })


@knowledge_bp.route("/delete/<int:id>", methods=["DELETE"])
@validate_uuid
def delete_knowledge(id):
    uuid = request.uuid
    
    result = knowledge_service.delete_knowledge(uuid, id)
    return jsonify(result)


@knowledge_bp.route("/detail/<int:id>", methods=["GET"])
@validate_uuid
def get_knowledge_detail(id):
    uuid = request.uuid
    
    result = knowledge_service.get_knowledge_detail(uuid, id)
    return jsonify(result)


@knowledge_bp.route("/search", methods=["GET"])
@validate_uuid
def search_knowledge():
    uuid = request.uuid
    query = request.args.get("query", "")
    
    if not query:
        return jsonify({"code": 400, "msg": "缺少搜索关键词"})
    
    result = knowledge_service.search_knowledge(uuid, query)
    return jsonify(result)
