from flask import request

def get_uuid():
    """从请求头获取UUID"""
    uid = request.headers.get('X-User-UUID')
    if not uid:
        # 尝试从参数获取
        data = request.get_json(silent=True)
        if data:
            uid = data.get('uuid')
    return uid
