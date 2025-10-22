# -*- coding: utf-8 -*-
"""
基于RAG架构的私人AI知识库 - 命令行界面
"""

import os
import sys
from dotenv import load_dotenv
from knowledge_base_service import KnowledgeBaseService

# 加载环境变量
load_dotenv()

# ================== 全局配置区 ==================
API_KEY = os.getenv("API_KEY", "")
LLM_URL = os.getenv("LLM_URL", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "Qwen3-32B-FP16")

# Ollama嵌入模型配置
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "nomic-embed-text:latest")

# 文档路径配置
DOCUMENTS_DIRECTORY = os.getenv("DOCUMENTS_DIRECTORY", "../euroncap_pdfs")
VECTOR_DB_DIRECTORY = os.getenv("VECTOR_DB_DIRECTORY", "./euroncap_pdfs/chroma_db")

# 检索参数
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
RETRIEVE_K = int(os.getenv("RETRIEVE_K", "20"))

# ================== 主程序 ==================
def main():
    print("🚀 正在启动RAG知识库...")
    
    # 检查命令行参数
    force_rebuild = '--rebuild' in sys.argv
    
    # 初始化知识库服务
    kb_service = KnowledgeBaseService(
        api_key=API_KEY,
        llm_url=LLM_URL,
        llm_model_name=LLM_MODEL_NAME,
        embed_model_name=EMBED_MODEL_NAME,
        documents_directory=DOCUMENTS_DIRECTORY,
        vector_db_directory=VECTOR_DB_DIRECTORY,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        retrieve_k=RETRIEVE_K
    )
    
    # 初始化服务
    if not kb_service.initialize(force_rebuild=force_rebuild):
        print("❌ 知识库初始化失败，程序退出")
        sys.exit(1)
    
    # 进入问答循环
    print("\n✅ 知识库已就绪！输入 'exit' 或 'quit' 退出")
    print("💡 提示：您也可以通过Web界面访问: python web_api.py")
    
    while True:
        query = input("\n请输入您的问题: ").strip()
        
        if query.lower() in ['exit', 'quit']:
            print("正在退出程序...")
            break
            
        if not query:
            continue
            
        # 获取答案
        result = kb_service.ask_question(query)
        
        # 显示结果
        print("\n" + "="*50)
        print(f"🔍 问题: {query}")
        
        if result["success"]:
            print(f"📚 参考文档: {', '.join(result['sources'])}")
            print(f"🤖 答案:\n{result['answer']}")
        else:
            print(f"❌ 错误: {result['error']}")
            
        print("="*50 + "\n")

if __name__ == "__main__":
    main()