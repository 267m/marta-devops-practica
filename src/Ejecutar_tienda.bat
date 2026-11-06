@echo off
cd /d "%~dp0"
where py >/dev/null 2>/dev/null && (py main.py) || (python main.py)
pause
