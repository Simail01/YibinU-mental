# -------------------------- 全局配置模块 --------------------------
import os
import logging
from typing import Optional
from enum import Enum

import torch
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_BASE_DIR = os.path.join(BASE_DIR, "model")
ENV_FILE = os.path.join(BASE_DIR, ".env")


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = "default_password"
    name: str = "yibinu"
    charset: str = "utf8mb4"
    
    max_connections: int = 10
    min_cached: int = 2
    max_cached: int = 5
    
    @property
    def config_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.name,
            "charset": self.charset,
        }


class ModelSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    
    chinese_mentalbert_dir: str = Field(
        default_factory=lambda: os.path.join(MODEL_BASE_DIR, "Chinese-MentalBERT")
    )
    chatglm_6b_int4_dir: str = Field(
        default_factory=lambda: os.path.join(MODEL_BASE_DIR, "Chatglm2-6b-int4")
    )
    bert_max_len: int = Field(default=512, alias="BERT_MAX_LEN")
    llm_max_len: int = Field(default=2048, alias="LLM_MAX_LEN")
    max_new_tokens: int = Field(default=1024, alias="MAX_NEW_TOKENS")


class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    
    chroma_db_dir: str = Field(
        default_factory=lambda: os.path.join(BASE_DIR, "data", "chroma_db")
    )
    embedding_model_name: str = "shibing624/text2vec-base-chinese"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        local_embedding_dir = os.path.join(MODEL_BASE_DIR, "text2vec-base-chinese")
        if os.path.exists(local_embedding_dir):
            self.embedding_model_name = local_embedding_dir


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=5000, alias="API_PORT")
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")
    log_level: LogLevel = Field(default=LogLevel.INFO, alias="LOG_LEVEL")


class FeatureFlags(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    
    enable_llm: bool = Field(default=True, alias="ENABLE_LLM")
    enable_emotion_analysis: bool = Field(default=True, alias="ENABLE_EMOTION_ANALYSIS")
    enable_rag: bool = Field(default=True, alias="ENABLE_RAG")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)


settings = Settings()

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

EMOTION_LABEL_MAP = {
    0: "中性",
    1: "焦虑",
    2: "抑郁",
    3: "烦躁",
    4: "自我否定"
}

RISK_LABEL_MAP = {
    0: "无风险",
    1: "低风险",
    2: "中风险",
    3: "高风险"
}

DB_CONFIG = settings.db.config_dict
CHINESE_MENTALBERT_DIR = settings.model.chinese_mentalbert_dir
CHATGLM_6B_INT4_DIR = settings.model.chatglm_6b_int4_dir
CHROMA_DB_DIR = settings.rag.chroma_db_dir
EMBEDDING_MODEL_NAME = settings.rag.embedding_model_name
BERT_MAX_LEN = settings.model.bert_max_len
LLM_MAX_LEN = settings.model.llm_max_len
MAX_NEW_TOKENS = settings.model.max_new_tokens
API_HOST = settings.server.api_host
API_PORT = settings.server.api_port
DEBUG_MODE = settings.server.debug_mode
ENABLE_LLM = settings.features.enable_llm
ENABLE_EMOTION_ANALYSIS = settings.features.enable_emotion_analysis
ENABLE_RAG = settings.features.enable_rag

logging.basicConfig(
    level=getattr(logging, settings.server.log_level.value),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_db_config() -> dict:
    return settings.db.config_dict


def is_llm_enabled() -> bool:
    return settings.features.enable_llm


def is_emotion_analysis_enabled() -> bool:
    return settings.features.enable_emotion_analysis


def is_rag_enabled() -> bool:
    return settings.features.enable_rag
