# RAG知识库 - 基于RAG架构的私人AI知识库

这是一个基于RAG (Retrieval Augmented Generation) 架构的私人AI知识库系统，支持多种文档格式，提供命令行和Web界面两种使用方式。

## 功能特性

- 🔍 **多格式文档支持**: PDF、TXT、HTML、JSON、Markdown等
- 🤖 **智能问答**: 基于向量检索和LLM的准确回答
- 💻 **双界面支持**: 命令行界面和Web聊天界面
- 🚀 **可执行文件**: 支持打包为exe文件，无需Python环境
- 🔧 **灵活配置**: 支持环境变量和配置文件
- 📚 **文档溯源**: 显示答案来源的具体文档

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+和Ollama：

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Ollama (用于嵌入模型)
# Windows/Mac: 从 https://ollama.ai 下载安装
# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# 下载嵌入模型
ollama pull nomic-embed-text:latest
```

### 2. 配置设置

复制配置模板并填入实际配置：

```bash
cp .env.template .env
```

编辑 `.env` 文件，设置必要的配置：

```env
# LLM API配置 (必需)
API_KEY=your_api_key_here
LLM_URL=https://your-llm-service.com/v1/chat/completions
LLM_MODEL_NAME=Qwen3-32B-FP16

# 其他配置保持默认值即可
```

### 3. 准备文档

将文档放入指定目录（默认为 `../euroncap_pdfs`）：

```bash
mkdir -p ../euroncap_pdfs
# 将您的PDF、TXT、HTML等文档复制到此目录
```

## 使用方法

### 方式一：Python脚本

#### 命令行界面
```bash
# 启动CLI模式
python main.py cli

# 强制重建数据库
python main.py cli --rebuild
```

#### Web界面
```bash
# 启动Web服务 (默认端口8000)
python main.py web

# 指定端口启动
python main.py web --port 9000

# 调试模式启动
python main.py web --debug
```

### 方式二：直接运行

#### 命令行界面
```bash
python private_ai_knowledge_base_cli.py
```

#### Web API服务
```bash
python web_api.py --host 0.0.0.0 --port 8000
```

### 方式三：可执行文件

生成exe文件：

```bash
# 创建打包脚本
python build_exe.py

# Windows用户
build.bat

# Linux/Mac用户
./build.sh
```

运行生成的exe文件：
- CLI版本：`dist/rag_knowledge_base/rag_knowledge_base_cli.exe`
- Web版本：`dist/rag_knowledge_base/rag_knowledge_base_web.exe`

## API接口

Web模式提供以下REST API接口：

### 健康检查
```http
GET /health
```

### 系统状态
```http
GET /api/status
```

### 问答接口
```http
POST /api/ask
Content-Type: application/json

{
    "question": "您的问题"
}
```

### 重建数据库
```http
POST /api/rebuild
```

### 聊天界面
访问 `http://localhost:8000/` 使用Web聊天界面

## 目录结构

```
rag_ask/
├── main.py                           # 主启动器
├── private_ai_knowledge_base_cli.py  # CLI版本
├── web_api.py                        # Web API服务
├── knowledge_base_service.py         # 核心服务类
├── build_exe.py                      # 打包脚本生成器
├── requirements.txt                  # Python依赖
├── .env.template                     # 配置模板
├── static/
│   └── chat.html                     # Web聊天界面
└── dist/                             # 打包输出目录
```

## 配置说明

| 配置项 | 描述 | 默认值 |
|--------|------|--------|
| API_KEY | LLM API密钥 | (必需) |
| LLM_URL | LLM服务URL | (必需) |
| LLM_MODEL_NAME | LLM模型名称 | Qwen3-32B-FP16 |
| EMBED_MODEL_NAME | 嵌入模型名称 | nomic-embed-text:latest |
| DOCUMENTS_DIRECTORY | 文档目录 | ../euroncap_pdfs |
| VECTOR_DB_DIRECTORY | 向量数据库目录 | ./euroncap_pdfs/chroma_db |
| CHUNK_SIZE | 文本块大小 | 1000 |
| CHUNK_OVERLAP | 文本块重叠 | 150 |
| RETRIEVE_K | 检索文档数量 | 20 |

## 故障排除

### 常见问题

1. **ImportError: No module named 'xxx'**
   - 确保已安装所有依赖：`pip install -r requirements.txt`

2. **向量数据库创建失败**
   - 检查文档目录是否存在且包含文档
   - 确保Ollama服务正在运行：`ollama serve`

3. **LLM调用失败**
   - 验证API_KEY和LLM_URL配置是否正确
   - 检查网络连接

4. **exe文件运行失败**
   - 确保目标机器上有必要的运行库
   - 将配置文件(.env)放在exe文件同一目录

### 获取帮助

如果遇到问题，请检查：
1. 配置文件是否正确设置
2. Ollama服务是否正常运行
3. 文档目录是否包含有效文档
4. 网络连接是否正常

## 许可证

本项目基于MIT许可证开源。