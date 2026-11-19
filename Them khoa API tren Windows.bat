@echo off
rem Luu khoa API cua Gemini va ElevenLabs vao Windows Credential Manager (dich vu "xuong-long-tieng").
rem Khoa khong bao gio nam trong tep nao cua xuong. De trong roi Enter de bo qua mot dich vu.
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PY=%LOCALAPPDATA%\xuong-long-tieng\venv-chung\Scripts\python.exe"
if not exist "%PY%" goto chua_cai
"%PY%" tools\them_khoa.py
echo.
pause
exit /b
:chua_cai
echo May nay chua cai xuong: bam dup "Cai dat tren Windows.bat" truoc.
pause
exit /b 1
