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

echo [1/2] Building SynAptIp LCR Control...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --distpath "%DIST_DIR%" --workpath "%BUILD_ROOT%\nyquist_analyzer" "nyquist_analyzer.spec"
if errorlevel 1 (
    echo [ERROR] LCR Control build failed.
    exit /b 1
)

echo [2/2] Building SynAptIp DC Bias Probe...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --distpath "%DIST_DIR%" --workpath "%BUILD_ROOT%\dc_bias_probe" "dc_bias_probe.spec"
if errorlevel 1 (
    echo [ERROR] DC Bias Probe build failed.
    exit /b 1
)

echo.
echo Build complete.
echo Executables:
if exist "%DIST_DIR%\SynAptIp_LCR_Control.exe" echo   %DIST_DIR%\SynAptIp_LCR_Control.exe
if exist "%DIST_DIR%\SynAptIp_DC_Bias_Probe.exe" echo   %DIST_DIR%\SynAptIp_DC_Bias_Probe.exe

echo.
echo Build artifacts:
echo   Dist:  %DIST_DIR%
echo   Build: %BUILD_ROOT%
endlocal
