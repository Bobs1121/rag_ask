# -*- coding: utf-8 -*-
"""
PyInstaller打包配置脚本
用于生成RAG知识库的可执行文件
"""

import os
import sys
import shutil
from pathlib import Path

# PyInstaller规格文件内容
SPEC_CONTENT = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件和静态资源
datas = [
    ('static', 'static'),
    ('.env.template', '.'),
]

# 隐藏导入
hiddenimports = [
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.uvloop',
    'langchain_community.document_loaders',
    'langchain_community.embeddings',
    'langchain_chroma',
    'langchain_ollama',
    'bs4',
    'pypdfium2',
    'fastapi',
    'pydantic',
    'starlette',
    'onnxruntime',
    'sentence_transformers',
    'chromadb',
]

# CLI应用配置
cli_a = Analysis(
    ['private_ai_knowledge_base_cli.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

cli_pyz = PYZ(cli_a.pure, cli_a.zipped_data, cipher=block_cipher)

cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    [],
    exclude_binaries=True,
    name='rag_knowledge_base_cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# Web API应用配置
web_a = Analysis(
    ['web_api.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

web_pyz = PYZ(web_a.pure, web_a.zipped_data, cipher=block_cipher)

web_exe = EXE(
    web_pyz,
    web_a.scripts,
    [],
    exclude_binaries=True,
    name='rag_knowledge_base_web',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# 收集所有文件到dist目录
coll = COLLECT(
    cli_exe,
    cli_a.binaries,
    cli_a.zipfiles,
    cli_a.datas,
    web_exe,
    web_a.binaries,
    web_a.zipfiles,
    web_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='rag_knowledge_base',
)
'''

def create_build_script():
    """创建打包脚本"""
    
    # Windows批处理脚本
    windows_script = '''@echo off
echo 正在安装依赖...
pip install -r requirements.txt

echo 正在生成可执行文件...
pyinstaller --clean rag_knowledge_base.spec

echo 复制配置文件...
copy .env.template dist\\rag_knowledge_base\\.env.template

echo 打包完成！
echo 可执行文件位置：
echo   CLI版本: dist\\rag_knowledge_base\\rag_knowledge_base_cli.exe  
echo   Web版本: dist\\rag_knowledge_base\\rag_knowledge_base_web.exe

pause
'''

    # Linux/Mac脚本
    unix_script = '''#!/bin/bash
echo "正在安装依赖..."
pip install -r requirements.txt

echo "正在生成可执行文件..."
pyinstaller --clean rag_knowledge_base.spec

echo "复制配置文件..."
cp .env.template dist/rag_knowledge_base/.env.template

echo "设置执行权限..."
chmod +x dist/rag_knowledge_base/rag_knowledge_base_cli
chmod +x dist/rag_knowledge_base/rag_knowledge_base_web

echo "打包完成！"
echo "可执行文件位置："
echo "  CLI版本: dist/rag_knowledge_base/rag_knowledge_base_cli"
echo "  Web版本: dist/rag_knowledge_base/rag_knowledge_base_web"
'''

    # 写入spec文件
    with open('rag_knowledge_base.spec', 'w', encoding='utf-8') as f:
        f.write(SPEC_CONTENT)
    
    # 写入构建脚本
    with open('build.bat', 'w', encoding='utf-8') as f:
        f.write(windows_script)
    
    with open('build.sh', 'w', encoding='utf-8') as f:
        f.write(unix_script)
    
    # 设置Unix脚本执行权限
    if os.name != 'nt':
        os.chmod('build.sh', 0o755)
    
    print("✅ 打包脚本创建完成！")
    print("Windows用户运行: build.bat")
    print("Linux/Mac用户运行: ./build.sh")

if __name__ == "__main__":
    create_build_script()