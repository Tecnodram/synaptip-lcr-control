@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "ACTIVATE_BAT=%ROOT_DIR%.venv\Scripts\activate.bat"
set "VENV_PYTHON=%ROOT_DIR%.venv\Scripts\python.exe"
set "PYTHON_EXE=python"
set "DIST_DIR=%ROOT_DIR%dist"
set "BUILD_ROOT=%ROOT_DIR%build"
set "SPEC_FILE=lcr_control_v2_3.spec"

if exist "%ACTIVATE_BAT%" (
    call "%ACTIVATE_BAT%"
)

if exist "%VENV_PYTHON%" (
    set "PYTHON_EXE=%VENV_PYTHON%"
)

if not exist "%ROOT_DIR%%SPEC_FILE%" (
    echo [ERROR] Missing spec file: %ROOT_DIR%%SPEC_FILE%
    exit /b 1
)

echo Cleaning previous build artifacts...
if exist "%BUILD_ROOT%" rmdir /s /q "%BUILD_ROOT%" >nul 2>&1
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%" >nul 2>&1
for /d /r "%ROOT_DIR%" %%D in (__pycache__) do (
    if exist "%%D" rmdir /s /q "%%D" >nul 2>&1
)

echo Building SynAptIp LCR Control V2.3 Stable...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean --distpath "%DIST_DIR%" --workpath "%BUILD_ROOT%\lcr_control_v2_3" "%SPEC_FILE%"
if errorlevel 1 (
    echo [ERROR] V2.3 build failed.
    exit /b 1
)

echo.
echo Build complete.
if exist "%DIST_DIR%\SynAptIp_LCR_Control_V2_3.exe" (
    echo Executable: %DIST_DIR%\SynAptIp_LCR_Control_V2_3.exe
) else (
    echo [ERROR] Executable not found after build.
    exit /b 1
)

endlocal
