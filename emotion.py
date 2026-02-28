import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# -------------------------- 1. 配置基础参数 --------------------------
# 本地Chinese-MentalBERT模型目录（替换为你实际的模型文件夹路径）
MODEL_DIR = "./model/Chinese-MentalBERT"  
# 标签映射（需与你微调时的标签定义一致，示例为情感倾向标签）
LABEL_MAP = {
    0: "中性",
    1: "焦虑",
    2: "抑郁",
    3: "烦躁"
}
# 测试文本（大学生心理健康相关场景）
TEST_TEXT = "我最近一个月都不想和同学说话，上课注意力集中不了，总觉得自己什么事都做不好，甚至有点不想上学了"


# -------------------------- 2. 加载本地模型与分词器 --------------------------
# 加载本地分词器（自动读取目录内的vocab.txt）
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
# 加载本地序列分类模型（自动读取config.json和pytorch_model.bin）
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)

# 设备配置（优先使用GPU）
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = model.to(device)


# -------------------------- 3. 文本编码与模型推理 --------------------------
def predict_mental_emotion(text):
    # 1. 文本编码（与微调时的参数一致：max_len、padding、truncation）
    encoding = tokenizer(
        text,
        add_special_tokens=True,
        max_length=128,  # 需与微调时的max_len保持一致
        padding="max_length",
        truncation=True,
        return_tensors="pt"  # 返回PyTorch张量
    ).to(device)  # 移至GPU/CPU

    # 2. 模型推理（关闭梯度计算，节省显存）
    model.eval()
    with torch.no_grad():
        outputs = model(
            input_ids=encoding["input_ids"],
            attention_mask=encoding["attention_mask"]
        )
    # 3. 解析预测结果（取logits最大值对应的标签）
    logits = outputs.logits
    predicted_label = torch.argmax(logits, dim=1).item()
    emotion = LABEL_MAP[predicted_label]
    
    return {
        "测试文本": text,
        "预测情感倾向": emotion
    }


# -------------------------- 4. 执行测试并输出结果 --------------------------
result = predict_mental_emotion(TEST_TEXT)
print("测试结果：")
for k, v in result.items():
    print(f"{k}：{v}")