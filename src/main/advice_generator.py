# -------------------------- 建议生成模块 --------------------------
import logging
import torch
from transformers import AutoTokenizer, AutoModel
from config import CHATGLM_6B_INT4_DIR, DEVICE, LLM_MAX_LEN, MAX_NEW_TOKENS

# 配置日志
logger = logging.getLogger(__name__)

class AdviceGenerator:
    def __init__(self, model_dir=None, device=None, max_seq_length=None, max_new_tokens=None,
                 temperature=0.7, top_p=0.95, repetition_penalty=1.1):
        """
        初始化建议生成器
        :param model_dir: 模型路径，默认从config读取。如果为 'mock'，则不加载模型。
        :param device: 运行设备，默认从config读取
        :param max_seq_length: 最大序列长度，默认从config读取
        :param max_new_tokens: 最大生成长度，默认从config读取
        """
        self.model_dir = model_dir or CHATGLM_6B_INT4_DIR
        self.device = device or DEVICE
        self.max_seq_length = 8192
        self.max_new_tokens = 2048
        self.temperature = 0.7
        self.top_p = 0.9
        self.repetition_penalty = 1.1
        self.max_rag_context_length = 4096
        self.max_prompt_length = 4096
        
        self.tokenizer = None
        self.model = None
        
        if self.model_dir == 'mock':
             logger.info("⚠️ 建议生成器运行在 MOCK 模式，不加载实际模型")
        else:
            logger.info(f"正在初始化建议生成器，使用模型: {self.model_dir}, 设备: {self.device}")
            self._load_model()

    def _load_model(self):
        """加载ChatGLM模型与分词器"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_dir,
                trust_remote_code=True,
                local_files_only=True
            )
            self.model = AutoModel.from_pretrained(
                self.model_dir,
                trust_remote_code=True,
                local_files_only=True,
                device_map="auto" if self.device.type == "cuda" else None
            )
            
            if self.device.type != "cuda":
                 self.model = self.model.to(self.device).float() # CPU模式通常需要float32
            
            self.model = self.model.eval()

            # 补充兼容属性 (针对某些ChatGLM版本)
            if hasattr(self.model.config, 'num_layers') and not hasattr(self.model.config, 'num_hidden_layers'):
                self.model.config.num_hidden_layers = self.model.config.num_layers
            
            # 兼容新版transformers: 添加all_tied_weights_keys属性
            if not hasattr(self.model, 'all_tied_weights_keys'):
                self.model.all_tied_weights_keys = []
                
            logger.info("✅ 建议生成模型加载成功")
        except Exception as e:
            logger.error(f"❌ 建议生成模型加载失败: {str(e)}")
            # 这里不抛出异常，允许服务在无模型情况下启动（降级处理），或者由上层决定是否退出
            # raise RuntimeError(f"建议生成模型加载失败：{str(e)}")
            self.model = None # 标记为不可用

    def _build_prompt(self, user_text, emotion, risk, scl90_summary=None, rag_context=None, deep_thinking=False, conversation_history=None):
        """构建结构化提示词模板 - 专业心理医生身份"""
        
        system_instruction = """你是一位资深心理咨询师，拥有丰富的临床经验和专业知识。你的角色是：
- 以专业、温暖、共情的态度与来访者沟通
- 运用心理学理论和技术帮助来访者理解自己的情绪和行为
- 提供科学、实用的心理调适建议
- 在必要时引导来访者寻求专业帮助

重要原则：
1. 你不是在提供医疗诊断，而是在进行心理支持和辅导
2. 始终保持专业边界，不替代医生或精神科专家的角色
3. 对于严重心理问题，必须建议来访者寻求专业医疗帮助"""

        history_context = ""
        if conversation_history:
            history_context = f"""
【历史对话记录】
{conversation_history}
（请基于以上历史对话，保持对话的连贯性和上下文理解）
"""

        user_profile = f"""
【来访者档案】
主诉问题：{user_text}
情感状态：{emotion}
风险等级：{risk}"""
        
        if scl90_summary:
            user_profile += f"\n心理测评参考：{scl90_summary}"
            
        context_info = ""
        if rag_context:
            context_info = f"""
【专业知识参考】
{rag_context}"""
            
        generation_guidelines = """
【咨询回应指南】

一、开场共情（必须）
- 用温暖、理解的语气回应来访者的感受
- 表达对其困扰的认可和接纳
- 示例："我理解你现在感到...，这种感觉确实让人很难受。"

二、问题分析
- 运用心理学视角分析问题的可能成因
- 帮助来访者看到问题背后的心理机制
- 可引用【专业知识参考】中的内容增强专业性

三、具体建议（3-5条）
针对来访者的情况，给出具体、可操作的建议：
- 情绪调节技巧（如正念呼吸、情绪日记等）
- 认知调整方法（如识别负面思维模式）
- 行为改变策略（如渐进式暴露、行为激活）
- 社会支持建议（如与信任的人沟通）

四、风险干预（根据风险等级）
- 【高风险/中风险】：必须明确建议"建议您尽快前往学校心理咨询中心或寻求专业心理医生的帮助，这是对自己负责的表现。"
- 【低风险/无风险】：鼓励其继续关注自身心理健康，必要时寻求支持

五、结束语
- 表达对来访者的信心和鼓励
- 提醒可以随时继续沟通
- 附上免责声明：以上建议基于心理咨询视角，仅供参考。如持续感到不适，请寻求专业心理帮助。"""

        if deep_thinking:
            generation_guidelines += """

【深度思考模式补充】
在回应前，请先进行以下深度分析：
1. 心理动力学分析：探索问题可能的潜意识根源
2. 认知行为分析：识别可能存在的认知扭曲
3. 发展心理学视角：考虑成长经历对当前问题的影响
4. 制定阶段性咨询计划建议

请展示你的专业分析过程，让来访者更深入地理解自己。"""

        prompt = f"{system_instruction}\n{user_profile}{context_info}\n{generation_guidelines}"
        return prompt.strip()

    def generate(self, user_text, emotion, risk, scl90_summary=None, rag_context=None, deep_thinking=False, conversation_history=None):
        """
        生成个性化心理健康建议
        """
        if self.model_dir == 'mock':
             mock_response = """【MOCK 响应】
             感谢您的分享。这只是一个模拟响应，因为后端正在以无模型模式运行。
             
             通常，我会根据您的情感分析结果、风险评估和SCL-90历史记录，为您提供定制化的建议。
             
             建议如下：
             1. 保持规律作息。
             2. 尝试与朋友倾诉。
             3. 适当进行户外运动。
             
             本建议仅供参考，不能替代专业医疗诊断。
             """
             if deep_thinking:
                 mock_response = "【MOCK 深度思考模式】\n正在深入分析您的心理机制...\n\n" + mock_response.replace("【MOCK 响应】", "")
             return mock_response

        if self.model is None or self.tokenizer is None:
            logger.warning("模型未加载，返回默认提示")
            return "抱歉，心理咨询助手当前正如火如荼地进行维护中，暂时无法生成详细建议。请稍后再试，或直接联系学校心理咨询中心。"

        # 1. 初步构建 Prompt
        prompt = self._build_prompt(user_text, emotion, risk, scl90_summary, rag_context, deep_thinking, conversation_history)
        
        # 2. Token 长度检查与截断 (简单策略：如果过长，丢弃 RAG 上下文)
        try:
            inputs = self.tokenizer([prompt], return_tensors="pt")
            input_len = len(inputs["input_ids"][0])
            
            # 预留 max_new_tokens 给生成
            max_input_len = self.max_seq_length - self.max_new_tokens
            
            if input_len > max_input_len:
                logger.warning(f"Prompt token 长度 ({input_len}) 超过限制 ({max_input_len})，尝试移除 RAG 上下文")
                # 重新构建不带 RAG 的 prompt
                prompt = self._build_prompt(user_text, emotion, risk, scl90_summary, rag_context=None, deep_thinking=deep_thinking)
                
                # 二次检查
                inputs = self.tokenizer([prompt], return_tensors="pt")
                input_len = len(inputs["input_ids"][0])
                if input_len > max_input_len:
                     logger.warning(f"移除 RAG 后 Prompt 仍过长 ({input_len})，截断用户输入")
                     # 极端情况：截断用户输入
                     allowed_user_len = max_input_len - 500 # 预留给系统指令
                     if allowed_user_len > 0:
                         prompt = self._build_prompt(user_text[:allowed_user_len] + "...", emotion, risk, scl90_summary, rag_context=None, deep_thinking=deep_thinking)
        except Exception as e:
            logger.warning(f"Token 长度检查失败: {e}，将尝试直接生成")

        try:
            # 使用简单的生成方式
            inputs = self.tokenizer([prompt], return_tensors="pt")
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # 直接使用generate方法，尝试禁用cache
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=False,
                )
            
            # 解码输出
            response = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            
            # 后处理：确保免责声明存在
            final_advice = response.strip()
            disclaimer = "本建议仅供参考，不能替代专业医疗诊断。若持续感到不适，请寻求专业帮助。"
            if "本建议仅供参考" not in final_advice and "免责声明" not in final_advice:
                final_advice += f"\n\n{disclaimer}"
                
            return final_advice
        except Exception as e:
            logger.error(f"建议生成过程中发生错误: {str(e)}")
            return "生成建议时遇到了一些技术问题，请稍后重试。如果情况紧急，请立即联系辅导员或心理中心。"
