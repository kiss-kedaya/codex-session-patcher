#!/bin/bash
# 打包脚本 - 生成跨平台二进制文件

set -e

VERSION="1.3.1"
DIST_DIR="dist"

echo "=== Codex Session Patcher 打包脚本 ==="
echo "版本: $VERSION"

# 清理旧的构建文件
echo "清理旧构建..."
rm -rf build/ dist/ *.egg-info

# 安装依赖
echo "安装打包依赖..."
pip install pyinstaller

# 构建 CLI 版本
echo "构建 CLI 可执行文件..."
pyinstaller codex-patcher.spec --clean

# 重命名输出
if [ -d "dist/codex-patcher" ]; then
    echo "打包完成: dist/codex-patcher/"
    ls -la dist/codex-patcher/
fi

# 创建压缩包
echo "创建分发包..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "linux"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win32"* ]]; then
    PLATFORM="windows"
else
    PLATFORM="unknown"
fi

ARCHIVE_NAME="codex-patcher-${VERSION}-${PLATFORM}"
cd dist
if [ -d "codex-patcher" ]; then
    mv codex-patcher "$ARCHIVE_NAME"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        zip -r "${ARCHIVE_NAME}.zip" "$ARCHIVE_NAME"
    elif [[ "$OSTYPE" == "linux"* ]]; then
        tar -czvf "${ARCHIVE_NAME}.tar.gz" "$ARCHIVE_NAME"
    elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win32"* ]]; then
        # Windows 下用 7z 或 zip
        zip -r "${ARCHIVE_NAME}.zip" "$ARCHIVE_NAME"
    fi
    echo "分发包已创建: dist/${ARCHIVE_NAME}.zip (或 .tar.gz)"
fi
cd ..

echo "=== 打包完成 ==="