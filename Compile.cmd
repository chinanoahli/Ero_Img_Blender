@echo off

del Run.exe
pyinstaller Run.py --upx-dir=.\upx -y --onefile
move .\dist\Run.exe .
del Run.spec
rd /s /q .\build .\dist

pause
