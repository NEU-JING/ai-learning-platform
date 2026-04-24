@echo off
chcp 65001 >nul
REM AI学习平台一键启动脚本 (Windows)
REM 支持开发环境快速启动

setlocal EnableDelayedExpansion

REM 项目根目录
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

REM 颜色设置
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM 打印函数
:print_info
echo %INFO% %~1
goto :eof

:print_success
echo %SUCCESS% %~1
goto :eof

:print_warning
echo %WARNING% %~1
goto :eof

:print_error
echo %ERROR% %~1
goto :eof

REM 检查依赖
:check_dependencies
call :print_info "检查依赖..."

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python 未安装或未添加到PATH"
    exit /b 1
)

call :print_success "依赖检查完成"
goto :eof

REM 检查并创建虚拟环境
:setup_venv
call :print_info "设置Python虚拟环境..."

cd /d "%BACKEND_DIR%"

if not exist "venv" (
    call :print_info "创建虚拟环境..."
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
call :print_info "安装后端依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

call :print_success "虚拟环境设置完成"
goto :eof

REM 启动后端
:start_backend
call :print_info "启动后端服务..."

cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat

REM 检查端口是否被占用
netstat -ano | findstr :8000 >nul
if not errorlevel 1 (
    call :print_warning "端口8000已被占用"
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 启动后端
start /B cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > %TEMP%\ai-learning-backend.log 2>&1"

REM 等待后端启动
call :print_info "等待后端启动..."
for /L %%i in (1,1,30) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if not errorlevel 1 (
        call :print_success "后端服务已启动: http://localhost:8000"
        goto :eof
    )
    timeout /t 1 /nobreak >nul
)

call :print_error "后端启动超时"
goto :eof

REM 启动前端
:start_frontend
call :print_info "启动前端服务..."

cd /d "%FRONTEND_DIR%"

REM 检查端口是否被占用
netstat -ano | findstr :3000 >nul
if not errorlevel 1 (
    call :print_warning "端口3000已被占用"
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 使用Python HTTP服务器
start /B cmd /c "python -m http.server 3000 > %TEMP%\ai-learning-frontend.log 2>&1"

call :print_success "前端服务已启动: http://localhost:3000"
goto :eof

REM 停止服务
:stop_services
call :print_info "停止服务..."

REM 停止占用8000和3000端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /PID %%a /F >nul 2>&1
)

call :print_success "所有服务已停止"
goto :eof

REM 查看状态
:status
call :print_info "服务状态检查..."

REM 检查后端
curl -s http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    call :print_success "后端服务运行中: http://localhost:8000"
) else (
    call :print_error "后端服务未运行"
)

REM 检查前端
curl -s http://localhost:3000 >nul 2>&1
if not errorlevel 1 (
    call :print_success "前端服务运行中: http://localhost:3000"
) else (
    call :print_error "前端服务未运行"
)
goto :eof

REM 显示帮助
:show_help
echo AI学习平台启动脚本 (Windows)
echo.
echo 用法: start.bat [命令]
echo.
echo 命令:
echo     start       启动所有服务（默认）
echo     stop        停止所有服务
echo     restart     重启所有服务
echo     status      查看服务状态
echo     help        显示帮助信息
echo.
echo 示例:
echo     start.bat              启动所有服务
echo     start.bat start        启动所有服务
echo     start.bat stop         停止所有服务
echo     start.bat restart      重启所有服务
echo.
echo 访问地址:
echo     前端: http://localhost:3000
echo     后端: http://localhost:8000
echo     API文档: http://localhost:8000/docs
goto :eof

REM 主函数
if "%~1"=="" goto :do_start
if "%~1"=="start" goto :do_start
if "%~1"=="stop" goto :do_stop
if "%~1"=="restart" goto :do_restart
if "%~1"=="status" goto :do_status
if "%~1"=="help" goto :do_help
if "%~1"=="--help" goto :do_help
if "%~1"=="-h" goto :do_help
goto :unknown

:do_start
call :print_info "🚀 AI学习平台启动脚本"
call :check_dependencies
if errorlevel 1 exit /b 1
call :setup_venv
call :start_backend
call :start_frontend
echo.
call :print_success "所有服务已启动！"
echo.
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
call :print_info "使用 'start.bat stop' 停止服务"
goto :eof

:do_stop
call :stop_services
goto :eof

:do_restart
call :stop_services
timeout /t 2 /nobreak >nul
goto :do_start

:do_status
call :status
goto :eof

:do_help
call :show_help
goto :eof

:unknown
call :print_error "未知命令: %~1"
call :show_help
exit /b 1
