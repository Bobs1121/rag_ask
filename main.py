# -*- coding: utf-8 -*-
"""
RAG知识库主启动器
支持CLI和Web两种模式
"""

import sys
import argparse
import os
from dotenv import load_dotenv

def main():
    """主函数"""
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="RAG知识库 - 基于RAG架构的私人AI知识库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py cli                    # 启动命令行界面
  python main.py cli --rebuild          # 重建数据库后启动CLI
  python main.py web                    # 启动Web服务 (默认端口8000)
  python main.py web --port 9000        # 在指定端口启动Web服务
  python main.py web --debug            # 调试模式启动Web服务
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='运行模式')
    
    # CLI模式
    cli_parser = subparsers.add_parser('cli', help='命令行界面模式')
    cli_parser.add_argument('--rebuild', action='store_true', help='强制重建向量数据库')
    
    # Web模式
    web_parser = subparsers.add_parser('web', help='Web服务模式')
    web_parser.add_argument('--host', default=os.getenv('WEB_HOST', '0.0.0.0'), help='服务器主机地址')
    web_parser.add_argument('--port', type=int, default=int(os.getenv('WEB_PORT', '8000')), help='服务器端口')
    web_parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return
    
    # 设置环境变量用于子模块
    if hasattr(args, 'rebuild') and args.rebuild:
        os.environ['FORCE_REBUILD'] = 'true'
    
    try:
        if args.mode == 'cli':
            print("🖥️  启动命令行界面模式...")
            from private_ai_knowledge_base_cli import main as cli_main
            cli_main()
            
        elif args.mode == 'web':
            print("🌐 启动Web服务模式...")
            print(f"📍 地址: http://{args.host}:{args.port}")
            print(f"📖 API文档: http://{args.host}:{args.port}/docs")
            print(f"💬 聊天界面: http://{args.host}:{args.port}/")
            print("按 Ctrl+C 停止服务")
            
            from web_api import run_server
            run_server(host=args.host, port=args.port, debug=args.debug)
            
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()