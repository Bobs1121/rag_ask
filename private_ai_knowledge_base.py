# -*- coding: utf-8 -*-
"""
基于RAG架构的私人AI知识库
"""

import os
import sys
import shutil
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFium2Loader
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredHTMLLoader,BSHTMLLoader, JSONLoader
from langchain_core.documents import Document
import logging
import requests
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

# ================== 全局配置区 ==================
API_KEY = 
LLM_URL = 
LLM_MODEL_NAME = 

# Ollama嵌入模型配置
EMBED_MODEL_NAME = "nomic-embed-text:latest"

# 文档路径配置
DOCUMENTS_DIRECTORY = "../euroncap_pdfs"
VECTOR_DB_DIRECTORY = "./euroncap_pdfs/chroma_db"

# 检索参数
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
RETRIEVE_K = 20

class SkipUnsupportedLoader(BaseLoader):
    """一个虚拟加载器，用于跳过不支持的文件类型并记录警告。"""
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        # 使用 logging.warning 而不是 print，这样在静默模式下可能也会显示
        logging.warning(f"SKIPPING unsupported file type: {self.file_path}")
        return []

def load_document(file_path):
    """根据文件扩展名选择加载器"""
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return PyPDFium2Loader(file_path)
    elif ext in [".html", ".htm"]:
        return BSHTMLLoader(file_path)
    elif ext == ".json":
        jq_schema = '.[]? | .mapping? | .[]? | .message?.content?.parts? | .[]? | select(type == "string" and length > 0)'
        return JSONLoader(
            file_path=file_path,
            jq_schema=jq_schema,
            text_content=True
        )
    elif ext in [".txt", ".md", ".py"]:
        return TextLoader(file_path)

    else:
        return SkipUnsupportedLoader(file_path)

# ================== 核心函数 ==================
def load_and_split_documents():
    """加载并分割文档"""
    print("正在加载文档...")
    
    # 自动创建文档目录
    if not os.path.exists(DOCUMENTS_DIRECTORY):
        os.makedirs(DOCUMENTS_DIRECTORY)
        print(f"已创建文档目录: {DOCUMENTS_DIRECTORY}")
    
    # 支持多种文档格式
    if not os.listdir(DOCUMENTS_DIRECTORY):
        raise ValueError(f"文档目录 {DOCUMENTS_DIRECTORY} 为空，请添加文本/PDF/HTML文件后再运行")
        
    print("------------------------")
    loader = DirectoryLoader(
        path=DOCUMENTS_DIRECTORY,
        glob="**/*",  # 支持文本/PDF/HTML
        show_progress=True,
        loader_cls=load_document,  # 修正为正确的参数名称
        silent_errors=True
    )
    
    documents = loader.load()
    print(f"已加载 {len(documents)} 个文档")
    # 文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True
    )
    
    split_docs = text_splitter.split_documents(documents)
    
    if not split_docs:
        raise ValueError("未生成任何文本块，请检查文档内容和分割参数")
    print(f"已分割为 {len(split_docs)} 个文本块")
    return split_docs

def create_or_load_vector_store(embeddings, force_rebuild):
    """
    (V2)
    创建或加载向量数据库。
    如果 'force_rebuild' 为 True，则强制删除并重建。
    否则，如果DB已存在，则加载；如果不存在，则创建。
    """
    if force_rebuild and os.path.exists(VECTOR_DB_DIRECTORY):
        print(f"检测到 --rebuild 参数，正在删除旧数据库: {VECTOR_DB_DIRECTORY}")
        shutil.rmtree(VECTOR_DB_DIRECTORY)

    if os.path.exists(VECTOR_DB_DIRECTORY) and os.listdir(VECTOR_DB_DIRECTORY):
        print("正在从本地加载现有向量数据库...")
        vectorstore = Chroma(
            persist_directory=VECTOR_DB_DIRECTORY,
            embedding_function=embeddings
        )
    else:
        print("未找到现有数据库，正在创建新的数据库...")
        try:
            docs = load_and_split_documents()
            print("正在创建并持久化向量数据库,请等待...")
            vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=embeddings,
                persist_directory=VECTOR_DB_DIRECTORY
            )
            print("数据库创建并持久化成功。")
        except ValueError as e:
            print(f"创建数据库时出错: {e}")
            print("程序将退出。")
            sys.exit(1) # 如果首次创建失败（例如目录为空），则退出
    
    return vectorstore

def retrieve_relevant_context(query, vectorstore):
    """检索相关上下文"""
    print("正在检索相关文档...")
    docs = vectorstore.similarity_search(query, k=RETRIEVE_K)
    
    # 提取上下文和源文件名
    context = "\n\n".join([d.page_content for d in docs])
    source_files = list(set([os.path.basename(d.metadata.get('source', '未知')) for d in docs]))
    
    return context, source_files

def get_answer_from_llm(query, context):
    """通过LLM生成答案"""
    messages = [
        {"role": "system", 
         "content": (
                "你是一个知识渊博、乐于助人的AI助手。\n"
                "请结合你自己的知识和下面提供的“上下文信息”来回答用户的问题。\n"
                "规则：\n"
                "1. 优先使用“上下文信息”来寻找答案。你的回答应该主要基于上下文。\n"
                "2. 仅当“上下文信息”为空或与问题完全无关时，你才可以使用你的通用知识来回答。\n"
                "3. 如果你使用了上下文信息，请在回答时保持简洁和相关性。\n"
                "4. 如果上下文信息为空，而你使用通用知识回答，请自然地回答，不要提及上下文。\n"  # /no think 
                #"5. 请不要在你的回答中包含任何 <think>...</think> 思考过程块，直接给出最终答案。" 
            )
        },
        {"role": "user", "content": f"上下文内容：\n{context}\n\n问题：\n{query}\n\n请给出准确、简洁的回答："}
    ]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        payload ={
                "model": "Qwen3-32B-FP16",
                "messages": messages,
                "stream": False
        }
        
        response = requests.post(LLM_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        print("✅ 响应状态码:", response.status_code)
        if "choices" in response_json and len(response_json["choices"]) > 0:
            assistant_message = response_json["choices"][0]["message"]
            assistant_content = assistant_message['content']  
        return assistant_content
    
    except Exception as e:
        return f"调用LLM时出错: {str(e)}", 0

# ================== 主程序 ==================
def main():
    # 初始化向量数据库
    force_rebuild = '--rebuild' in sys.argv
        # 1. 初始化嵌入模型
    print("正在初始化嵌入模型...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL_NAME)
    
    # 2. (V2) 加载或创建向量数据库
    vectorstore = create_or_load_vector_store(embeddings, force_rebuild)

    
    # 进入问答循环
    print("\n✅ 知识库已就绪！输入 'exit' 或 'quit' 退出")
    while True:
        query = input("\n请输入您的问题: ").strip()
        
        if query.lower() in ['exit', 'quit']:
            print("正在退出程序...")
            break
            
        if not query:
            continue
            
        # 检索上下文
        context, source_files = retrieve_relevant_context(query, vectorstore)
        
        # 获取答案
        answer = get_answer_from_llm(query, context)
        
        # 显示结果
        print("\n" + "="*50)
        print(f"🔍 问题: {query}")
        print(f"📚 参考文档: {', '.join(source_files)}")
        print(f"🤖 答案:\n{answer}")
        print("="*50 + "\n")

if __name__ == "__main__":
    main()

