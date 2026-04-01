@echo off
REM Windows 打包脚本 - 生成 exe 可执行文件

set VERSION=1.3.1
set DIST_DIR=dist

echo === Codex Session Patcher 打包脚本 ===
echo 版本: %VERSION%

REM 清理旧构建
echo 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info

REM 安装依赖
echo 安装打包依赖...
pip install pyinstaller

REM 构建 CLI 版本
echo 构建 CLI 可执行文件...
pyinstaller codex-patcher.spec --clean

REM 重命名输出
if exist dist\codex-patcher (
    echo 打包完成: dist\codex-patcher\
    dir dist\codex-patcher
)

REM 创建压缩包
set ARCHIVE_NAME=codex-patcher-%VERSION%-windows
cd dist
if exist codex-patcher (
    rename codex-patcher %ARCHIVE_NAME%
    REM 使用 PowerShell 创建 zip
    powershell Compress-Archive -Path %ARCHIVE_NAME% -DestinationPath %ARCHIVE_NAME%.zip
    echo 分发包已创建: dist\%ARCHIVE_NAME%.zip
)
cd ..

echo === 打包完成 ===