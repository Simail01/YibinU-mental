import os
import json
import logging
from datetime import datetime
from config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME, ENABLE_RAG

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入 LangChain 和 ChromaDB
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_core.documents import Document
    import chromadb
except ImportError as e:
    logger.warning(f"未检测到 LangChain 或 ChromaDB，RAG 功能将不可用。错误详情: {e}")
    Chroma = None
    HuggingFaceEmbeddings = None

class RAGService:
    def __init__(self, persist_directory=CHROMA_DB_DIR):
        self.persist_directory = persist_directory
        self.embedding_model = None
        self.vector_store = None
        
        if ENABLE_RAG and Chroma and HuggingFaceEmbeddings:
            try:
                # 初始化 Embedding 模型
                logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
                self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
                
                # 初始化 ChromaDB
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embedding_model,
                    collection_name="yibinu_knowledge"
                )
                logger.info("✅ RAG服务初始化成功")
            except Exception as e:
                logger.error(f"❌ RAG服务初始化失败: {e}")
                self.vector_store = None
        else:
            if not ENABLE_RAG:
                logger.info("⚠️ RAG服务已禁用 (ENABLE_RAG=False)")
            else:
                logger.warning("⚠️ 依赖缺失 (LangChain/ChromaDB)，RAG服务不可用")
            self.vector_store = None
    
    def add_knowledge(self, uuid, title, content, k_type="private"):
        """添加知识库内容"""
        if self.vector_store is None:
            return False
            
        metadata = {
            "uuid": uuid if k_type == "private" else "public",
            "type": k_type,
            "title": title,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            doc = Document(page_content=content, metadata=metadata)
            self.vector_store.add_documents([doc])
            # self.vector_store.persist() # 新版 ChromaDB 通常会自动持久化
            return True
        except Exception as e:
            logger.error(f"添加知识失败: {e}")
            return False

    def sync_scl90_result(self, uuid, summary):
        """同步 SCL-90 结果到向量库"""
        title = "SCL-90测评报告"
        content = f"用户最新的SCL-90测评结果摘要：{summary}"
        # 移除旧的 SCL-90 记录以避免重复干扰？目前 Chroma 暂不支持按 metadata 删除方便的 API (需 lookup ID)
        # 暂时直接添加，作为新的记录
        return self.add_knowledge(uuid, title, content, k_type="private")

    def search(self, uuid, query, k=5, score_threshold=0.5):
        """
        检索知识
        策略：检索 公共知识库 + 该用户的个人知识库
        """
        if not self.vector_store:
            return []

        try:
            # 1. 检索公共知识
            public_docs = self.vector_store.similarity_search_with_score(
                query, 
                k=k, 
                filter={"type": "public"}
            )
            
            # 2. 检索个人知识
            private_docs = self.vector_store.similarity_search_with_score(
                query, 
                k=k, 
                filter={"uuid": uuid}
            )
            
            # 合并结果 (doc, score)
            all_results = public_docs + private_docs
            
            # 过滤低相关性结果 (score 越小越相似，Chroma 默认是 L2 距离，或者是 cosine distance)
            # 假设是 cosine distance，范围 0-1 (0 是完全相同，1 是完全不同)
            # 如果是 L2，值可能大于 1
            # 这里我们假设 score 是距离，越小越好。我们可以设置一个阈值。
            # 为了保险，先不过滤，只排序。
            
            all_results.sort(key=lambda x: x[1]) # 按分数升序排序（距离越小越好）
            
            # 去重
            seen = set()
            final_docs = []
            for doc, score in all_results:
                if doc.page_content not in seen:
                    seen.add(doc.page_content)
                    final_docs.append(doc)
            
            return final_docs[:k*2] 
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

rag_service = RAGService()
