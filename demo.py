#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG知识库演示脚本
展示系统功能和使用方法
"""

import os
import sys
import time

def print_banner():
    print("=" * 60)
    print("🤖 RAG知识库系统演示")
    print("基于RAG架构的私人AI知识库")
    print("=" * 60)

def print_features():
    print("\n📋 主要功能:")
    print("  ✅ 多格式文档支持 (PDF, TXT, HTML, JSON, MD)")
    print("  ✅ 向量检索和语义搜索")
    print("  ✅ 大模型增强生成")
    print("  ✅ 命令行界面 (CLI)")
    print("  ✅ Web聊天界面")
    print("  ✅ REST API接口")
    print("  ✅ 可执行文件打包")

def print_usage():
    print("\n🚀 使用方法:")
    print("\n1. 配置环境:")
    print("   cp .env.template .env")
    print("   # 编辑 .env 文件，设置 API_KEY 和 LLM_URL")
    
    print("\n2. 准备文档:")
    print("   mkdir -p documents")
    print("   # 将PDF、TXT等文档放入documents目录")
    
    print("\n3. 启动方式:")
    print("   # 命令行模式")
    print("   python main.py cli")
    print("   ")
    print("   # Web服务模式")
    print("   python main.py web")
    print("   ")
    print("   # 指定端口")
    print("   python main.py web --port 9000")

def print_api_endpoints():
    print("\n🔌 API接口:")
    print("  GET  /health              - 健康检查")
    print("  GET  /api/status          - 系统状态")
    print("  POST /api/ask             - 问答接口")
    print("  POST /api/rebuild         - 重建数据库")
    print("  GET  /                    - Web聊天界面")
    print("  GET  /docs                - API文档")

def print_packaging():
    print("\n📦 打包为可执行文件:")
    print("  # 生成打包脚本")
    print("  python build_exe.py")
    print("  ")
    print("  # Windows用户")
    print("  build.bat")
    print("  ")
    print("  # Linux/Mac用户")
    print("  ./build.sh")
    print("  ")
    print("  # 输出文件:")
    print("  # dist/rag_knowledge_base/rag_knowledge_base_cli.exe")
    print("  # dist/rag_knowledge_base/rag_knowledge_base_web.exe")

def print_tech_stack():
    print("\n🛠️  技术栈:")
    print("  • LangChain - RAG架构框架")
    print("  • Chroma - 向量数据库")
    print("  • Ollama - 嵌入模型服务")
    print("  • FastAPI - Web API框架")
    print("  • PyInstaller - 打包工具")

def main():
    print_banner()
    print_features()
    print_usage()
    print_api_endpoints()
    print_packaging()
    print_tech_stack()
    
    print("\n" + "=" * 60)
    print("📖 详细文档请查看 README.md")
    print("🌐 Web界面演示: demo_chat.html")
    print("=" * 60)

if __name__ == "__main__":
    main()