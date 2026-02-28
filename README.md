# YibinU 大学生心理健康智能分析系统

## 1. 系统简介
YibinU 是一个专为大学生设计的心理健康智能分析系统，旨在通过数字化手段提供便捷、专业的心理健康服务。系统集成了专业的心理测评（SCL-90）、基于大模型的智能情感分析与咨询、以及个性化的知识库管理功能，能够为用户提供从评估到咨询的全方位心理支持。

## 2. 系统功能描述

### 2.1 心理测评模块 (SCL-90)
- **在线测评**：提供标准的 SCL-90 心理健康症状自评量表，包含 90 道题目。
- **自动评分**：根据用户回答自动计算 10 个因子分（躯体化、强迫症状、人际关系敏感等）及总分。
- **结果分析**：实时生成测评报告，直观展示各项指标得分，并提供初步的解释。
- **匿名保护**：采用 UUID 机制，用户无需注册即可进行测评，充分保护用户隐私。

### 2.2 智能咨询模块
- **情感分析**：利用 MentalBERT 模型对用户输入的文本进行情感倾向分析（焦虑、抑郁、烦躁等）和风险等级评估（无风险至高风险）。
- **AI 对话**：集成 ChatGLM2-6B 大语言模型，结合 RAG（检索增强生成）技术，根据用户的情感状态和测评结果，提供共情、专业的心理咨询建议。
- **上下文记忆**：系统具备多轮对话记忆功能，能够联系上下文提供连贯的咨询服务。

### 2.3 知识库管理
- **RAG 增强**：利用向量数据库（ChromaDB）存储心理健康知识，辅助 AI 生成更准确的建议。
- **个人知识库**：用户（在特定场景下）可以上传个人日记或备忘录，系统在咨询时会参考这些私有信息。
- **公共知识库**：系统内置专业的心理学知识，确保咨询内容的专业性和科学性。

### 2.4 用户管理
- **匿名访问**：系统核心功能支持免登录访问，通过浏览器指纹或本地存储生成的 UUID 标识用户身份。
- **历史记录**：支持本地查看对话历史和测评记录。

## 3. 技术栈

- **前端**：HTML5, CSS3, JavaScript (原生), Fetch API
- **后端**：Python Flask, Flask-CORS
- **AI 模型**：
  - 情感分析：Chinese-MentalBERT
  - 对话生成：ChatGLM2-6B (Int4 量化版)
  - Embedding：text2vec-base-chinese
- **数据库**：
  - 关系型数据库：MySQL (存储用户记录、测评结果、对话日志)
  - 向量数据库：ChromaDB (存储 RAG 知识库向量)
- **工具链**：LangChain, PyMySQL, Transformers

## 4. 服务器部署文档

### 4.1 环境准备
1.  **操作系统**：Windows / Linux (推荐 Ubuntu 20.04+)
2.  **Python 环境**：Python 3.8+ (建议使用 Anaconda 或 venv)
3.  **数据库**：MySQL 5.7+
4.  **硬件要求**：
    - 显存：至少 6GB (用于运行 ChatGLM2-6B Int4)
    - 内存：16GB+

### 4.2 部署步骤

#### 步骤 1：克隆项目
```bash
git clone <repository_url>
cd YibinU
```

#### 步骤 2：安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤 3：配置数据库
1. 确保 MySQL 服务已启动。
2. 创建数据库 `yibinu_db`。
3. 修改 `src/main/database.py` 中的数据库配置（host, user, password 等）。
4. 系统启动时会自动初始化表结构。

#### 步骤 4：准备模型文件
请将以下模型文件下载至 `d:\Idea_WorkSpace\YibinU\model\` 目录下（或修改 `APP .py` 中的路径配置）：
- `Chinese-MentalBERT`
- `ChatGLM2-6B-Int4`

#### 步骤 5：启动服务
```bash
# 启动后端服务
cd src/main
python "APP .py"
```
服务默认运行在 `http://localhost:5000`。

#### 步骤 6：访问前端
直接在浏览器中打开 `src/front/index.html` 即可开始使用。

## 5. API 接口简述

- `GET /api/scl90/questions`: 获取测评题目
- `POST /api/scl90/submit`: 提交测评答案
- `POST /api/mental_analysis`: 发送对话内容进行分析与回复
- `GET /api/dialogue/history`: 获取对话历史
- `DELETE /api/dialogue/history`: 清空对话历史
- `POST /api/knowledge/add`: 添加知识库内容
- `GET /api/knowledge/list`: 获取知识库列表

---
**注意**：首次运行时，系统会自动下载 Embedding 模型和初始化向量数据库，可能需要一定时间，请耐心等待。

## 6. 离线环境配置（模型下载）

为了在无外网环境（离线环境）下运行本系统，您需要提前下载所有必要的 AI 模型文件。

### 6.1 使用脚本一键下载

本项目提供了一个 Python 脚本 `download_models.py`，用于自动下载所有依赖模型。

**步骤：**

1.  确保已安装 `huggingface_hub`：
    ```bash
    pip install huggingface_hub
    ```
2.  在有外网的环境下运行下载脚本：
    ```bash
    python download_models.py
    ```
    该脚本会自动将以下模型下载到项目根目录下的 `model/` 文件夹中：
    - `Chinese-MentalBERT` (情感分析)
    - `Chatglm2-6b-int4` (对话大模型)
    - `text2vec-base-chinese` (向量嵌入模型)

3.  下载完成后，您可以将整个项目文件夹拷贝到离线环境中运行。系统会自动检测并使用本地模型。

**注意**：如果您在中国大陆地区下载速度较慢，可以设置环境变量 `HF_ENDPOINT` 使用镜像源：
```bash
# Windows PowerShell
$env:HF_ENDPOINT = "https://hf-mirror.com"
python download_models.py

# Linux / Mac
export HF_ENDPOINT=https://hf-mirror.com
python download_models.py
```
