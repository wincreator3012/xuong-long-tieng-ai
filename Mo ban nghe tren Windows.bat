@echo off
rem Mo Ban nghe trong trinh duyet: nghe tung doan, chon luot doc, ghi chu doc lai, ghep ban chinh, thi nghe mu.
rem Dong cua so nay de tat Ban nghe.
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PY=%LOCALAPPDATA%\xuong-long-tieng\venv-chung\Scripts\python.exe"
if not exist "%PY%" goto chua_cai
"%PY%" tools\ban_nghe\may_chu.py --cong 8768
exit /b
:chua_cai
echo May nay chua cai xuong: bam dup "Cai dat tren Windows.bat" truoc.
pause
exit /b 1
