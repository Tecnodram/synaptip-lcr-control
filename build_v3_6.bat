@echo off
setlocal

:: ============================================================
:: SynAptIp Nyquist Analyzer V3.6 -- Build Script
:: SynAptIp Technologies
:: AI, Scientific Software & Instrument Intelligence
:: ============================================================

set "ROOT_DIR=%~dp0"
set "ACTIVATE_BAT=%ROOT_DIR%.venv\Scripts\activate.bat"
set "VENV_PYTHON=%ROOT_DIR%.venv\Scripts\python.exe"
set "PYTHON_EXE=python"
set "DIST_DIR=%ROOT_DIR%dist"
set "BUILD_ROOT=%ROOT_DIR%build"
set "SPEC_FILE=lcr_control_v3_6.spec"
set "EXE_NAME=SynAptIp_Nyquist_Analyzer_V3_6.exe"
set "APP_DIST_DIR=%DIST_DIR%\SynAptIp_Nyquist_Analyzer_V3_6"

:: Activate venv if present
if exist "%ACTIVATE_BAT%" (
    call "%ACTIVATE_BAT%"
)

if exist "%VENV_PYTHON%" (
    set "PYTHON_EXE=%VENV_PYTHON%"
)

:: Verify spec file
if not exist "%ROOT_DIR%%SPEC_FILE%" (
    echo [ERROR] Missing spec file: %ROOT_DIR%%SPEC_FILE%
    exit /b 1
)

:: Verify dependencies
"%PYTHON_EXE%" -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing matplotlib...
    "%PYTHON_EXE%" -m pip install matplotlib --quiet
)

"%PYTHON_EXE%" -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pandas...
    "%PYTHON_EXE%" -m pip install pandas --quiet
)

"%PYTHON_EXE%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller not installed. Run: pip install pyinstaller
    exit /b 1
)

echo.
echo ============================================================
echo  SynAptIp Nyquist Analyzer V3.6 -- Build Started
echo  SynAptIp Technologies
echo ============================================================
echo.

:: Clean previous V3.6 artifacts only
echo Cleaning previous V3.6 build artifacts...
if exist "%BUILD_ROOT%\lcr_control_v3_6" rmdir /s /q "%BUILD_ROOT%\lcr_control_v3_6" >nul 2>&1
if exist "%DIST_DIR%\%EXE_NAME%" del /f /q "%DIST_DIR%\%EXE_NAME%" >nul 2>&1
if exist "%APP_DIST_DIR%" rmdir /s /q "%APP_DIST_DIR%" >nul 2>&1

:: Clean __pycache__ in src_v3_6 only
for /d /r "%ROOT_DIR%src_v3_6" %%D in (__pycache__) do (
    if exist "%%D" rmdir /s /q "%%D" >nul 2>&1
)

:: Build
echo Building SynAptIp Nyquist Analyzer V3.6...
echo.
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean ^
    --distpath "%DIST_DIR%" ^
    --workpath "%BUILD_ROOT%\lcr_control_v3_6" ^
    "%SPEC_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] V3.6 build FAILED.
    exit /b 1
)

if not exist "%DIST_DIR%\%EXE_NAME%" (
    echo [ERROR] Executable not found after build.
    exit /b 1
)

:: Package release folder
echo Packaging release folder...
mkdir "%APP_DIST_DIR%" >nul 2>&1
copy /y "%DIST_DIR%\%EXE_NAME%" "%APP_DIST_DIR%\%EXE_NAME%" >nul

if exist "%ROOT_DIR%assets" (
    xcopy "%ROOT_DIR%assets" "%APP_DIST_DIR%\assets\" /e /i /y >nul
)
if exist "%ROOT_DIR%example_data" (
    xcopy "%ROOT_DIR%example_data" "%APP_DIST_DIR%\example_data\" /e /i /y >nul
)

echo.
echo ============================================================
if exist "%APP_DIST_DIR%\%EXE_NAME%" (
    echo  BUILD COMPLETE
    echo  Output: %APP_DIST_DIR%\%EXE_NAME%
) else (
    echo [ERROR] Packaging failed.
    exit /b 1
)
echo ============================================================
echo.
echo  Previous versions untouched:
if exist "%DIST_DIR%\SynAptIp_Nyquist_Analyzer_V3_5.exe" (
    echo   [OK] V3.5 exe present
)
if exist "%DIST_DIR%\SynAptIp_LCR_Control_V3.exe" (
    echo   [OK] V3 exe present
)
echo.
pause
