@echo off
echo 正在安装依赖...
pip install -r requirements.txt

echo 正在生成可执行文件...
pyinstaller --clean rag_knowledge_base.spec

echo 复制配置文件...
copy .env.template dist\rag_knowledge_base\.env.template

echo 打包完成！
echo 可执行文件位置：
echo   CLI版本: dist\rag_knowledge_base\rag_knowledge_base_cli.exe  
echo   Web版本: dist\rag_knowledge_base\rag_knowledge_base_web.exe

pause
