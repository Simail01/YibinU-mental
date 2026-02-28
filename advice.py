import torch
from transformers import AutoTokenizer, AutoModel

# ===================== 全局配置（请根据你的本地环境修改）=====================
# 本地ChatGLM2-6B-int4模型文件夹的绝对路径（关键！）
LOCAL_MODEL_PATH = "D:\Idea_WorkSpace\YibinU\model\Chatglm2-6b-int4"  # 替换为你的模型路径（正斜杠）
# LOCAL_MODEL_PATH = "D:\\Models\\chatglm2-6b-int4"  # 双反斜杠格式也可

# 设备配置（自动识别GPU/CPU，优先使用GPU）
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# 生成参数（适配6G显存，兼顾效果和运行稳定性）
MAX_LENGTH = 1024  # 最大序列长度（输入+输出）
TEMPERATURE = 0.7  # 生成随机性（0~1，值越大越灵活，越小越严谨）
TOP_P = 0.95       # 采样阈值，控制生成多样性
REPETITION_PENALTY = 1.1  # 重复惩罚，避免生成重复内容

# ===================== 加载本地模型和Tokenizer（核心步骤）=====================
def load_local_chatglm():
    """加载本地ChatGLM2-6B-int4模型和分词器"""
    try:
        # 加载分词器（local_files_only=True：仅加载本地文件，不联网）
        tokenizer = AutoTokenizer.from_pretrained(
            LOCAL_MODEL_PATH,
            trust_remote_code=True,  # 必须开启，加载自定义ChatGLM分词器
            local_files_only=True    # 关键：禁用网络下载，仅读取本地文件
        )
        
        # 加载模型（无需4bit量化，本地int4模型已量化，6G显存足够）
        model = AutoModel.from_pretrained(
            LOCAL_MODEL_PATH,
            trust_remote_code=True,  # 必须开启，加载自定义ChatGLM模型
            local_files_only=True,   # 关键：禁用网络下载，仅读取本地文件
            device_map="auto"        # 自动分配设备（优先GPU，不足部分用CPU）
        ).to(DEVICE).eval()  # eval()：进入评估模式，关闭训练相关层（必加）
        
        print(f"✅ 模型和分词器加载成功！运行设备：{DEVICE}")
        print(f"🔧 GPU名称：{torch.cuda.get_device_name(0) if DEVICE == 'cuda' else '无GPU'}")
        return tokenizer, model
    except Exception as e:
        raise RuntimeError(f"❌ 加载失败：{str(e)}")

# ===================== 核心对话/生成方法=====================
def chatglm_chat(tokenizer, model, query, history=None):
    """
    调用本地ChatGLM2模型进行对话/生成
    :param tokenizer: 加载好的分词器
    :param model: 加载好的模型
    :param query: 用户查询/提示词（Prompt）
    :param history: 对话历史（多轮对话用，单次生成传None/空列表）
    :return: 模型回复、更新后的对话历史
    """
    if history is None:
        history = []
    
    try:
        # 调用官方chat()方法（最稳定，无需手动处理底层细节）
        response, updated_history = model.chat(
            tokenizer=tokenizer,
            query=query,
            history=history,
            max_length=MAX_LENGTH,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repetition_penalty=REPETITION_PENALTY
        )
        return response, updated_history
    except Exception as e:
        raise Exception(f"❌ 生成失败：{str(e)}")

# ===================== 测试运行（单次生成+多轮对话示例）=====================
if __name__ == "__main__":
    # 1. 加载本地模型
    try:
        tokenizer, model = load_local_chatglm()
    except RuntimeError as e:
        print(e)
        exit(1)
    
    # 2. 示例1：单次生成（心理健康建议，贴合你的业务需求）
    print("=" * 60)
    print("示例1：单次生成心理健康建议")
    print("=" * 60)
    user_query = """
    你是一名专业的大学生心理健康支持助手，仅提供支持性、指导性的日常调节建议，不进行任何专业心理疾病诊断，不推荐任何药物。
    请根据以下信息，为该大学生生成贴合其生活场景的个性化建议：
    1.  学生自述：最近期末考试压力大，晚上经常失眠，上课注意力不集中，还容易和室友吵架。
    2.  情感倾向：焦虑、烦躁
    3.  心理风险等级：低风险

    生成要求：
    1.  语气温和、亲切，符合大学生的认知水平；
    2.  分点列出建议，每条建议具体可操作；
    3.  结尾添加固定免责声明：“本建议仅为心理健康支持参考，不能替代专业医疗诊断，若持续情绪不适请及时寻求专业帮助。”
    """
    response, _ = chatglm_chat(tokenizer, model, user_query)
    print(f"✅ 模型回复：\n{response}\n")
    
    # 3. 示例2：多轮对话（基于历史上下文）
    print("=" * 60)
    print("示例2：多轮对话")
    print("=" * 60)
    history = []
    # 第一轮对话
    query1 = "刚才你提到的睡前放松方法，具体怎么做深呼吸？"
    response1, history = chatglm_chat(tokenizer, model, query1, history)
    print(f"用户：{query1}")
    print(f"模型：{response1}\n")
    
    # 第二轮对话（基于第一轮历史）
    query2 = "除了深呼吸，还有其他适合在宿舍做的睡前放松活动吗？"
    response2, history = chatglm_chat(tokenizer, model, query2, history)
    print(f"用户：{query2}")
    print(f"模型：{response2}")