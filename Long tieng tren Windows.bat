@echo off
rem Chay moi viec long tieng Claude da xep: sinh tieng, go bang nguoc de kiem, cham luot, ghep ban nhap.
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "ENV=%LOCALAPPDATA%\xuong-long-tieng"
set "HF_HOME=%ENV%\hf"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "PY=%ENV%\venv-chung\Scripts\python.exe"
if not exist "%PY%" goto chua_cai
"%PY%" tools\hang_doi.py chay
if errorlevel 1 goto co_loi
echo.
echo Long tieng xong. Bam dup "Mo ban nghe tren Windows.bat" de nghe, hoac quay lai Claude va nhan: da long tieng xong.
pause
exit /b
:co_loi
echo.
echo Co viec bi loi. Quay lai Claude va nhan: long tieng bi loi (log o Du an\_tam\long-tieng\log).
pause
exit /b 1
:chua_cai
echo May nay chua cai xuong: bam dup "Cai dat tren Windows.bat" truoc.
pause
exit /b 1
