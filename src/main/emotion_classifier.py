# -------------------------- 情感分类模块 --------------------------
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class EmotionClassifier:
    def __init__(self, model_dir, emotion_label_map, risk_label_map, device, max_seq_length):
        self.model_dir = model_dir
        self.emotion_label_map = emotion_label_map
        self.risk_label_map = risk_label_map
        self.device = device
        self.max_seq_length = max_seq_length
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载情感分类模型与分词器"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_dir,
                num_labels=len(self.emotion_label_map),
                ignore_mismatched_sizes=True
            ).to(self.device).eval()
            print("✅ 情感分类模型加载成功")
        except Exception as e:
            raise RuntimeError(f"情感分类模型加载失败：{str(e)}")

    def _encode_text(self, text):
        """文本编码处理"""
        try:
            return self.tokenizer(
                text,
                add_special_tokens=True,
                max_length=self.max_seq_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            ).to(self.device)
        except Exception as e:
            raise Exception(f"文本编码失败：{str(e)}")

    def _heuristic_risk_assessment(self, emotion_label):
        """
        基于情感类别的启发式风险评估
        由于缺乏专门训练的风险分类头，使用规则映射作为替代方案
        """
        # 0: "中性", 1: "焦虑", 2: "抑郁", 3: "烦躁", 4: "自我否定"
        # 0: "无风险", 1: "低风险", 2: "中风险", 3: "高风险"
        
        mapping = {
            "中性": "无风险",
            "焦虑": "低风险",   # 焦虑通常是低风险，除非严重
            "烦躁": "低风险",
            "抑郁": "中风险",   # 抑郁倾向视为中风险
            "自我否定": "高风险" # 自我否定可能涉及自伤，视为高风险
        }
        return mapping.get(emotion_label, "未知")

    def discriminate(self, user_text):
        """
        判别情感倾向与风险等级
        :param user_text: 用户输入文本
        :return: (emotion_result, risk_result)
        """
        # 文本编码
        encoding = self._encode_text(user_text)
        if encoding.get("input_ids") is None or encoding["input_ids"].shape[0] == 0:
            raise Exception("编码结果无效，input_ids为空")

        # 情感倾向判别
        with torch.no_grad():
            try:
                outputs = self.model(
                    input_ids=encoding["input_ids"],
                    attention_mask=encoding["attention_mask"]
                )
                emotion_label_id = torch.argmax(outputs.logits, dim=1).item()
                emotion_result = self.emotion_label_map[emotion_label_id]
            except Exception as e:
                raise Exception(f"情感倾向推理失败：{str(e)}")

        # 风险等级判别 (使用启发式规则替代随机初始化的分类头)
        risk_result = self._heuristic_risk_assessment(emotion_result)
        
        # 如果需要更复杂的逻辑，可以结合 SCL-90 分数，但这通常在业务层处理

        return emotion_result, risk_result
