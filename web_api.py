# -*- coding: utf-8 -*-
"""
FastAPI Web Application for RAG Knowledge Base
基于FastAPI的RAG知识库Web应用
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from dotenv import load_dotenv

from knowledge_base_service import KnowledgeBaseService

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="RAG Knowledge Base API",
    description="基于RAG架构的私人AI知识库API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型
class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    sources: List[str] = []

class StatusResponse(BaseModel):
    success: bool
    initialized: bool
    documents_directory: str
    vector_db_directory: str
    embed_model: str
    llm_model: str
    has_api_config: bool

# 全局知识库服务实例
kb_service = None

def get_kb_service() -> KnowledgeBaseService:
    """获取知识库服务实例"""
    global kb_service
    if kb_service is None:
        # 从环境变量或默认值获取配置
        kb_service = KnowledgeBaseService(
            api_key=os.getenv("API_KEY", ""),
            llm_url=os.getenv("LLM_URL", ""),
            llm_model_name=os.getenv("LLM_MODEL_NAME", "Qwen3-32B-FP16"),
            embed_model_name=os.getenv("EMBED_MODEL_NAME", "nomic-embed-text:latest"),
            documents_directory=os.getenv("DOCUMENTS_DIRECTORY", "../euroncap_pdfs"),
            vector_db_directory=os.getenv("VECTOR_DB_DIRECTORY", "./euroncap_pdfs/chroma_db"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
            retrieve_k=int(os.getenv("RETRIEVE_K", "20"))
        )
    return kb_service

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化知识库"""
    logger.info("正在启动RAG知识库服务...")
    service = get_kb_service()
    
    # 检查是否需要强制重建
    force_rebuild = os.getenv("FORCE_REBUILD", "false").lower() == "true"
    
    try:
        success = service.initialize(force_rebuild=force_rebuild)
        if success:
            logger.info("✅ 知识库服务启动成功!")
        else:
            logger.warning("⚠️  知识库服务启动时遇到问题，但服务仍可用于配置")
    except Exception as e:
        logger.error(f"❌ 知识库服务启动失败: {str(e)}")

# API路由
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回聊天界面"""
    return FileResponse("static/chat.html")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "RAG Knowledge Base API is running"}

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """获取系统状态"""
    try:
        service = get_kb_service()
        status = service.get_status()
        return StatusResponse(success=True, **status)
    except Exception as e:
        logger.error(f"获取状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """提问端点"""
    try:
        service = get_kb_service()
        if not service._initialized:
            raise HTTPException(
                status_code=503, 
                detail="知识库服务未初始化，请检查配置或联系管理员"
            )
        
        result = service.ask_question(request.question)
        
        if result["success"]:
            return QuestionResponse(
                success=True,
                question=result["question"],
                answer=result["answer"],
                sources=result["sources"]
            )
        else:
            return QuestionResponse(
                success=False,
                error=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理问题时出错: {str(e)}")
        return QuestionResponse(
            success=False,
            error=f"处理问题时出错: {str(e)}"
        )

@app.post("/api/rebuild")
async def rebuild_database():
    """重建向量数据库"""
    try:
        service = get_kb_service()
        success = service.initialize(force_rebuild=True)
        
        if success:
            return {"success": True, "message": "向量数据库重建成功"}
        else:
            return {"success": False, "message": "向量数据库重建失败"}
            
    except Exception as e:
        logger.error(f"重建数据库时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 静态文件服务
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

def run_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """运行服务器"""
    uvicorn.run(
        "web_api:app" if not debug else "web_api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG知识库Web API服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    print(f"🚀 正在启动RAG知识库Web API服务...")
    print(f"📍 地址: http://{args.host}:{args.port}")
    print(f"📖 API文档: http://{args.host}:{args.port}/docs")
    print(f"💬 聊天界面: http://{args.host}:{args.port}/")
    
    run_server(host=args.host, port=args.port, debug=args.debug)