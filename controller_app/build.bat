@REM Building using pyinstaller and keeping only the exe
pyinstaller app.py --windowed --onefile -i "icon.png" -n "Pixel Controller"
copy "dist\Pixel Controller.exe" .
rmdir /s /q build
rmdir /s /q dist
del ".\Pixel Controller.spec"