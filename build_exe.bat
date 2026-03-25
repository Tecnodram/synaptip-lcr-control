@echo off
setlocal

REM Legacy alias. Prefer build_all.bat for reproducible Windows packaging.
call "%~dp0build_all.bat"
set EXIT_CODE=%ERRORLEVEL%
endlocal & exit /b %EXIT_CODE%
