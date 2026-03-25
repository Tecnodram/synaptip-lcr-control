@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "VENV_PYTHON=%ROOT_DIR%.venv\Scripts\python.exe"
set "DIST_DIR=%ROOT_DIR%dist"
set "BUILD_ROOT=%ROOT_DIR%build"

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Missing virtual environment Python: %VENV_PYTHON%
    echo Create the venv and install requirements first.
    exit /b 1
)

echo Building SynAptIp LCR Control V2.1...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --distpath "%DIST_DIR%" --workpath "%BUILD_ROOT%\lcr_control_v2_1" "lcr_control_v2_1.spec"
if errorlevel 1 (
    echo [ERROR] V2.1 build failed.
    exit /b 1
)

echo.
echo Build complete.
if exist "%DIST_DIR%\SynAptIp_LCR_Control_V2_1.exe" echo Executable: %DIST_DIR%\SynAptIp_LCR_Control_V2_1.exe

endlocal
