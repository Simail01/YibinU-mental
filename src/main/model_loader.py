import logging
from config import (
    CHINESE_MENTALBERT_DIR, CHATGLM_6B_INT4_DIR, 
    EMOTION_LABEL_MAP, RISK_LABEL_MAP, 
    DEVICE, BERT_MAX_LEN, LLM_MAX_LEN, MAX_NEW_TOKENS,
    ENABLE_LLM, ENABLE_EMOTION_ANALYSIS
)
from emotion_classifier import EmotionClassifier
from advice_generator import AdviceGenerator

logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self):
        self.emotion_classifier = None
        self.advice_generator = None

    def load_models(self):
        print(f"当前运行设备：{DEVICE}")
        print("开始加载模型与分词器...")
        
        # 初始化情感分类器
        if ENABLE_EMOTION_ANALYSIS:
            try:
                self.emotion_classifier = EmotionClassifier(
                    model_dir=CHINESE_MENTALBERT_DIR,
                    emotion_label_map=EMOTION_LABEL_MAP,
                    risk_label_map=RISK_LABEL_MAP,
                    device=DEVICE,
                    max_seq_length=BERT_MAX_LEN
                )
            except Exception as e:
                logger.error(f"⚠️ 情感分类器加载失败: {e}")
                self.emotion_classifier = None
        else:
            print("⚠️ 情感分析已禁用 (ENABLE_EMOTION_ANALYSIS=False)")
            self.emotion_classifier = None
        
        # 初始化建议生成器
        if ENABLE_LLM:
            try:
                self.advice_generator = AdviceGenerator(
                    model_dir=CHATGLM_6B_INT4_DIR,
                    device=DEVICE,
                    max_seq_length=LLM_MAX_LEN,
                    max_new_tokens=MAX_NEW_TOKENS,
                    temperature=0.7,
                    top_p=0.95,
                    repetition_penalty=1.1
                )
            except Exception as e:
                logger.error(f"⚠️ 建议生成器加载失败: {e}")
                self.advice_generator = None
        else:
             print("⚠️ LLM已禁用 (ENABLE_LLM=False)，建议生成功能将使用模拟响应")
             # 使用 mock 模式初始化
             self.advice_generator = AdviceGenerator(model_dir='mock')

        print("✅ 模型加载完成")

# Global instance
model_loader = ModelLoader()
