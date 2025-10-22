# -*- coding: utf-8 -*-
"""
RAG Knowledge Base Service
核心知识库服务类
"""

import os
import sys
import shutil
from typing import List, Tuple, Optional
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFium2Loader
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredHTMLLoader, BSHTMLLoader, JSONLoader
from langchain_core.documents import Document
import logging
import requests
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class SkipUnsupportedLoader(BaseLoader):
    """一个虚拟加载器，用于跳过不支持的文件类型并记录警告。"""
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        logging.warning(f"SKIPPING unsupported file type: {self.file_path}")
        return []


class KnowledgeBaseService:
    """RAG知识库服务类"""
    
    def __init__(self, 
                 api_key: str = "",
                 llm_url: str = "",
                 llm_model_name: str = "Qwen3-32B-FP16",
                 embed_model_name: str = "nomic-embed-text:latest",
                 documents_directory: str = "../euroncap_pdfs",
                 vector_db_directory: str = "./euroncap_pdfs/chroma_db",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 150,
                 retrieve_k: int = 20):
        """
        初始化知识库服务
        
        Args:
            api_key: LLM API密钥
            llm_url: LLM服务URL
            llm_model_name: LLM模型名称
            embed_model_name: 嵌入模型名称
            documents_directory: 文档目录路径
            vector_db_directory: 向量数据库目录路径
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
            retrieve_k: 检索返回的文档数量
        """
        self.api_key = api_key
        self.llm_url = llm_url
        self.llm_model_name = llm_model_name
        self.embed_model_name = embed_model_name
        self.documents_directory = documents_directory
        self.vector_db_directory = vector_db_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retrieve_k = retrieve_k
        
        self.embeddings = None
        self.vectorstore = None
        self._initialized = False
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """
        初始化知识库服务
        
        Args:
            force_rebuild: 是否强制重建向量数据库
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            print("正在初始化嵌入模型...")
            self.embeddings = OllamaEmbeddings(model=self.embed_model_name)
            
            print("正在初始化向量数据库...")
            self.vectorstore = self._create_or_load_vector_store(force_rebuild)
            
            self._initialized = True
            print("✅ 知识库服务初始化成功！")
            return True
            
        except Exception as e:
            print(f"❌ 知识库服务初始化失败: {str(e)}")
            return False
    
    def load_document(self, file_path: str):
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
    
    def _load_and_split_documents(self):
        """加载并分割文档"""
        print("正在加载文档...")
        
        # 自动创建文档目录
        if not os.path.exists(self.documents_directory):
            os.makedirs(self.documents_directory)
            print(f"已创建文档目录: {self.documents_directory}")
        
        # 支持多种文档格式
        if not os.listdir(self.documents_directory):
            raise ValueError(f"文档目录 {self.documents_directory} 为空，请添加文本/PDF/HTML文件后再运行")
            
        print("------------------------")
        loader = DirectoryLoader(
            path=self.documents_directory,
            glob="**/*",
            show_progress=True,
            loader_cls=self.load_document,
            silent_errors=True
        )
        
        documents = loader.load()
        print(f"已加载 {len(documents)} 个文档")
        
        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        
        split_docs = text_splitter.split_documents(documents)
        
        if not split_docs:
            raise ValueError("未生成任何文本块，请检查文档内容和分割参数")
        print(f"已分割为 {len(split_docs)} 个文本块")
        return split_docs
    
    def _create_or_load_vector_store(self, force_rebuild: bool):
        """创建或加载向量数据库"""
        if force_rebuild and os.path.exists(self.vector_db_directory):
            print(f"检测到强制重建参数，正在删除旧数据库: {self.vector_db_directory}")
            shutil.rmtree(self.vector_db_directory)

        if os.path.exists(self.vector_db_directory) and os.listdir(self.vector_db_directory):
            print("正在从本地加载现有向量数据库...")
            vectorstore = Chroma(
                persist_directory=self.vector_db_directory,
                embedding_function=self.embeddings
            )
        else:
            print("未找到现有数据库，正在创建新的数据库...")
            try:
                docs = self._load_and_split_documents()
                print("正在创建并持久化向量数据库,请等待...")
                vectorstore = Chroma.from_documents(
                    documents=docs,
                    embedding=self.embeddings,
                    persist_directory=self.vector_db_directory
                )
                print("数据库创建并持久化成功。")
            except ValueError as e:
                print(f"创建数据库时出错: {e}")
                raise e
        
        return vectorstore
    
    def retrieve_relevant_context(self, query: str) -> Tuple[str, List[str]]:
        """检索相关上下文"""
        if not self._initialized:
            raise RuntimeError("知识库服务未初始化，请先调用initialize()方法")
        
        print("正在检索相关文档...")
        docs = self.vectorstore.similarity_search(query, k=self.retrieve_k)
        
        # 提取上下文和源文件名
        context = "\n\n".join([d.page_content for d in docs])
        source_files = list(set([os.path.basename(d.metadata.get('source', '未知')) for d in docs]))
        
        return context, source_files
    
    def get_answer_from_llm(self, query: str, context: str) -> str:
        """通过LLM生成答案"""
        if not self.api_key or not self.llm_url:
            return "错误：LLM API配置不完整，请设置API_KEY和LLM_URL"
        
        messages = [
            {"role": "system", 
             "content": (
                    "你是一个知识渊博、乐于助人的AI助手。\n"
                    "请结合你自己的知识和下面提供的"上下文信息"来回答用户的问题。\n"
                    "规则：\n"
                    "1. 优先使用"上下文信息"来寻找答案。你的回答应该主要基于上下文。\n"
                    "2. 仅当"上下文信息"为空或与问题完全无关时，你才可以使用你的通用知识来回答。\n"
                    "3. 如果你使用了上下文信息，请在回答时保持简洁和相关性。\n"
                    "4. 如果上下文信息为空，而你使用通用知识回答，请自然地回答，不要提及上下文。\n"
                )
            },
            {"role": "user", "content": f"上下文内容：\n{context}\n\n问题：\n{query}\n\n请给出准确、简洁的回答："}
        ]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            payload = {
                "model": self.llm_model_name,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(self.llm_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            response_json = response.json()
            
            if "choices" in response_json and len(response_json["choices"]) > 0:
                assistant_message = response_json["choices"][0]["message"]
                assistant_content = assistant_message['content']
                return assistant_content
            else:
                return "错误：LLM响应格式不正确"
        
        except Exception as e:
            return f"调用LLM时出错: {str(e)}"
    
    def ask_question(self, query: str) -> dict:
        """
        询问问题并获取答案
        
        Args:
            query: 用户问题
            
        Returns:
            dict: 包含答案、参考文档等信息的字典
        """
        if not self._initialized:
            return {
                "success": False,
                "error": "知识库服务未初始化",
                "answer": None,
                "sources": []
            }
        
        try:
            # 检索上下文
            context, source_files = self.retrieve_relevant_context(query)
            
            # 获取答案
            answer = self.get_answer_from_llm(query, context)
            
            return {
                "success": True,
                "error": None,
                "question": query,
                "answer": answer,
                "sources": source_files,
                "context": context
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": None,
                "sources": []
            }
    
    def get_status(self) -> dict:
        """获取服务状态"""
        return {
            "initialized": self._initialized,
            "documents_directory": self.documents_directory,
            "vector_db_directory": self.vector_db_directory,
            "embed_model": self.embed_model_name,
            "llm_model": self.llm_model_name,
            "has_api_config": bool(self.api_key and self.llm_url)
        }