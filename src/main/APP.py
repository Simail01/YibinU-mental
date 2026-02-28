import logging
from flask import Flask
from flask_cors import CORS

from config import API_HOST, API_PORT, DEBUG_MODE
from model_loader import model_loader
from database import db_manager
from routes.scl90_routes import scl90_bp
from routes.analysis_routes import analysis_bp
from routes.knowledge_routes import knowledge_bp
from utils.logging_config import setup_logging, RequestLogger

setup_logging()

app = Flask(__name__)
CORS(app, resources=r"/*", supports_credentials=True)

RequestLogger(app)

logger = logging.getLogger(__name__)

model_loader.load_models()

try:
    db_manager._init_pool()
    if db_manager._available:
        db_manager.init_db()
    else:
        logger.warning("数据库不可用，部分功能将受限")
except Exception as e:
    logger.error(f"数据库初始化失败: {e}")

logger.info(f"所有模块初始化完成！后端服务就绪，监听端口 {API_PORT}...")

app.register_blueprint(scl90_bp, url_prefix='/api/scl90')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')

@app.route("/health", methods=["GET"])
def health_check():
    return {
        "code": 200,
        "msg": "ok",
        "data": {
            "database": db_manager.health_check(),
            "models": {
                "emotion": model_loader.emotion_classifier is not None,
                "llm": model_loader.advice_generator is not None
            }
        }
    }

if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE)
