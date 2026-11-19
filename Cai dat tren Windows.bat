@echo off
rem Cai hoac cap nhat xuong long tieng tren Windows: do may, dung moi truong Python, tai mo hinh cua may doc dang bat,
rem go mo hinh khong con dung, roi tu kiem. Bam lai bao nhieu lan cung duoc. Chi tiet: tools\cai_dat.py.
rem Moi thu cai vao %LOCALAPPDATA%\xuong-long-tieng (ngoai thu muc xuong).
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul
if not errorlevel 1 goto chay
echo == Cai cong cu uv, quan ly Python
powershell -NoProfile -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul
if errorlevel 1 goto loi_uv
:chay
uv run --no-project --python 3.12 tools\cai_dat.py %*
echo.
pause
exit /b
:loi_uv
echo Khong cai duoc uv: kiem tra mang roi bam dup lai tep nay.
pause
exit /b 1
