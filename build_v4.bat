@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "ACTIVATE_BAT=%ROOT_DIR%.venv\Scripts\activate.bat"
set "VENV_PYTHON=%ROOT_DIR%.venv\Scripts\python.exe"
set "BUNDLED_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "PYTHON_EXE=python"
set "DIST_DIR=%ROOT_DIR%dist"
set "BUILD_ROOT=%ROOT_DIR%build"
set "SPEC_FILE=lcr_control_v4.spec"
set "EXE_NAME=SynAptIp_Nyquist_Analyzer_V4.exe"
set "APP_DIST_DIR=%DIST_DIR%\SynAptIp_Nyquist_Analyzer_V4"

if exist "%ACTIVATE_BAT%" (
    call "%ACTIVATE_BAT%"
)

if exist "%VENV_PYTHON%" (
    set "PYTHON_EXE=%VENV_PYTHON%"
)
if /I "%PYTHON_EXE%"=="python" if exist "%BUNDLED_PYTHON%" (
    set "PYTHON_EXE=%BUNDLED_PYTHON%"
)

if not exist "%ROOT_DIR%%SPEC_FILE%" (
    echo [ERROR] Missing spec file: %ROOT_DIR%%SPEC_FILE%
    exit /b 1
)

"%PYTHON_EXE%" -V >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No working Python interpreter found.
    exit /b 1
)

"%PYTHON_EXE%" -c "import PySide6, serial, matplotlib, pandas, openpyxl, lxml, PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing project dependencies from requirements.txt...
    "%PYTHON_EXE%" -m pip install -r "%ROOT_DIR%requirements.txt"
    if errorlevel 1 (
        echo [ERROR] Failed to install project dependencies.
        exit /b 1
    )
)

"%PYTHON_EXE%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller not installed.
    exit /b 1
)

echo.
echo ============================================================
echo  SynAptIp Nyquist Analyzer V4 -- Build Started
echo ============================================================
echo.

if exist "%BUILD_ROOT%\lcr_control_v4" rmdir /s /q "%BUILD_ROOT%\lcr_control_v4" >nul 2>&1
if exist "%DIST_DIR%\%EXE_NAME%" del /f /q "%DIST_DIR%\%EXE_NAME%" >nul 2>&1
if exist "%APP_DIST_DIR%" rmdir /s /q "%APP_DIST_DIR%" >nul 2>&1

for /d /r "%ROOT_DIR%src_v4" %%D in (__pycache__) do (
    if exist "%%D" rmdir /s /q "%%D" >nul 2>&1
)

"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean ^
    --distpath "%DIST_DIR%" ^
    --workpath "%BUILD_ROOT%\lcr_control_v4" ^
    "%SPEC_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] V4 build FAILED.
    exit /b 1
)

if not exist "%DIST_DIR%\%EXE_NAME%" (
    echo [ERROR] Executable not found after build.
    exit /b 1
)

mkdir "%APP_DIST_DIR%" >nul 2>&1
copy /y "%DIST_DIR%\%EXE_NAME%" "%APP_DIST_DIR%\%EXE_NAME%" >nul

if exist "%ROOT_DIR%assets" (
    xcopy "%ROOT_DIR%assets" "%APP_DIST_DIR%\assets\" /e /i /y >nul
)
if exist "%ROOT_DIR%example_data" (
    xcopy "%ROOT_DIR%example_data" "%APP_DIST_DIR%\example_data\" /e /i /y >nul
)
if exist "%ROOT_DIR%example_outputs" (
    xcopy "%ROOT_DIR%example_outputs" "%APP_DIST_DIR%\example_outputs\" /e /i /y >nul
)
if exist "%ROOT_DIR%licenses" (
    xcopy "%ROOT_DIR%licenses" "%APP_DIST_DIR%\licenses\" /e /i /y >nul
)

if exist "%ROOT_DIR%README.md" (
    copy /y "%ROOT_DIR%README.md" "%APP_DIST_DIR%\" >nul
)
if exist "%ROOT_DIR%CHANGELOG.md" (
    copy /y "%ROOT_DIR%CHANGELOG.md" "%APP_DIST_DIR%\" >nul
)
if exist "%ROOT_DIR%LICENSE" (
    copy /y "%ROOT_DIR%LICENSE" "%APP_DIST_DIR%\" >nul
)

echo.
echo ============================================================
echo  SynAptIp Nyquist Analyzer V4 -- Build Complete
echo ============================================================
echo.
echo Release folder: %APP_DIST_DIR%
echo Executable:     %APP_DIST_DIR%\%EXE_NAME%
