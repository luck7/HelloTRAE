@echo off
chcp 65001 >nul
echo ==========================================
echo      Battle City - Pygame Zero
echo ==========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.x
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查 pgzero 是否安装
python -c "import pgzrun" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 Pygame Zero ...
    python -m pip install pgzero
    if errorlevel 1 (
        echo [错误] Pygame Zero 安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo [提示] Pygame Zero 安装完成
)

:: 运行游戏
echo [提示] 正在启动 Battle City ...
echo.
python -m pgzero.main main.py

if errorlevel 1 (
    echo.
    echo [错误] 游戏运行失败
    pause
)
