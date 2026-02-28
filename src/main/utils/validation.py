import logging
import re
from functools import wraps
from typing import Optional, Callable, Any

from flask import request, jsonify
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class SCL90SubmitRequest(BaseModel):
    answers: dict = Field(..., min_length=90)
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v):
        for qid, score in v.items():
            try:
                qid_int = int(qid)
                score_int = int(score)
                if qid_int < 1 or qid_int > 90:
                    raise ValueError(f"题目ID {qid} 超出范围 (1-90)")
                if score_int < 1 or score_int > 5:
                    raise ValueError(f"分数 {score} 超出范围 (1-5)")
            except (ValueError, TypeError):
                raise ValueError(f"无效的答案格式: {qid}={score}")
        return v


class MentalAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    deep_thinking: bool = False
    
    @field_validator('text')
    @classmethod
    def sanitize_text(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("文本不能为空")
        return v


class KnowledgeAddRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=10000)
    type: str = Field(default="private")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v not in ('public', 'private'):
            raise ValueError("类型必须是 public 或 private")
        return v


def validate_json(schema: type[BaseModel]):
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                json_data = request.get_json(silent=True)
                if json_data is None:
                    return jsonify({
                        "code": 400,
                        "msg": "请求体必须是有效的JSON格式"
                    }), 400
                
                validated = schema(**json_data)
                request.validated_data = validated
                
            except Exception as e:
                logger.warning(f"请求验证失败: {e}")
                return jsonify({
                    "code": 400,
                    "msg": f"参数验证失败: {str(e)}"
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_uuid(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from utils.request_utils import get_uuid
        uuid = get_uuid()
        if not uuid:
            return jsonify({
                "code": 401,
                "msg": "缺少用户标识 (UUID)"
            }), 401
        request.uuid = uuid
        return f(*args, **kwargs)
    return decorated_function


def sanitize_input(text: str, max_length: int = 5000) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    return text


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    from collections import defaultdict
    import time
    
    request_counts: dict = defaultdict(list)
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from utils.request_utils import get_uuid
            client_id = get_uuid() or request.remote_addr
            current_time = time.time()
            
            request_counts[client_id] = [
                t for t in request_counts[client_id]
                if current_time - t < window_seconds
            ]
            
            if len(request_counts[client_id]) >= max_requests:
                logger.warning(f"请求频率超限: {client_id}")
                return jsonify({
                    "code": 429,
                    "msg": "请求过于频繁，请稍后再试"
                }), 429
            
            request_counts[client_id].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
