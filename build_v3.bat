@echo off
setlocal

:: ============================================================
:: SynAptIp LCR Control V3 — Build Script
:: SynAptIp Technologies
:: AI, Scientific Software & Instrument Intelligence
:: ============================================================

set "ROOT_DIR=%~dp0"
set "ACTIVATE_BAT=%ROOT_DIR%.venv\Scripts\activate.bat"
set "VENV_PYTHON=%ROOT_DIR%.venv\Scripts\python.exe"
set "PYTHON_EXE=python"
set "DIST_DIR=%ROOT_DIR%dist"
set "BUILD_ROOT=%ROOT_DIR%build"
set "SPEC_FILE=lcr_control_v3.spec"
set "EXE_NAME=SynAptIp_LCR_Control_V3.exe"

:: Activate venv if present
if exist "%ACTIVATE_BAT%" (
    call "%ACTIVATE_BAT%"
)

if exist "%VENV_PYTHON%" (
    set "PYTHON_EXE=%VENV_PYTHON%"
)

:: Verify spec file exists
if not exist "%ROOT_DIR%%SPEC_FILE%" (
    echo [ERROR] Missing spec file: %ROOT_DIR%%SPEC_FILE%
    exit /b 1
)

:: Verify matplotlib is installed (required for JPG export)
"%PYTHON_EXE%" -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing matplotlib...
    "%PYTHON_EXE%" -m pip install matplotlib --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install matplotlib.
        exit /b 1
    )
)

:: Verify PyInstaller is installed
"%PYTHON_EXE%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed.
    echo Run: pip install pyinstaller
    exit /b 1
)

echo.
echo ============================================================
echo  SynAptIp LCR Control V3 -- Build Started
echo  SynAptIp Technologies
echo ============================================================
echo.

:: Clean previous V3 artifacts only (leave V2.3 dist untouched)
echo Cleaning previous V3 build artifacts...
if exist "%BUILD_ROOT%\lcr_control_v3" rmdir /s /q "%BUILD_ROOT%\lcr_control_v3" >nul 2>&1
if exist "%DIST_DIR%\%EXE_NAME%" del /f /q "%DIST_DIR%\%EXE_NAME%" >nul 2>&1

:: Clean __pycache__ in src_v3 only
for /d /r "%ROOT_DIR%src_v3" %%D in (__pycache__) do (
    if exist "%%D" rmdir /s /q "%%D" >nul 2>&1
)

:: Run PyInstaller
echo Building SynAptIp LCR Control V3...
echo.
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean ^
    --distpath "%DIST_DIR%" ^
    --workpath "%BUILD_ROOT%\lcr_control_v3" ^
    "%SPEC_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] V3 build FAILED. Check output above for details.
    exit /b 1
)

echo.
echo ============================================================
if exist "%DIST_DIR%\%EXE_NAME%" (
    echo  BUILD COMPLETE
    echo  Executable: %DIST_DIR%\%EXE_NAME%
) else (
    echo [ERROR] Executable not found after build.
    echo Expected: %DIST_DIR%\%EXE_NAME%
    exit /b 1
)
echo ============================================================
echo.
echo  V2.3 dist is untouched:
if exist "%DIST_DIR%\SynAptIp_LCR_Control_V2_3.exe" (
    echo   [OK] SynAptIp_LCR_Control_V2_3.exe present
) else (
    echo   [INFO] SynAptIp_LCR_Control_V2_3.exe not found (not built yet)
)
echo.

endlocal
