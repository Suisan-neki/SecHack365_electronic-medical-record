@echo off
echo デスクトップにショートカットを作成中...

set "currentDir=%~dp0"
set "desktop=%USERPROFILE%\Desktop"

echo [DesktopShortcut]
echo URL=file:///%currentDir%start_systems.bat
echo IconFile=%currentDir%start_systems.bat
echo IconIndex=0
echo HotKey=0
echo IDList=
echo [InternetShortcut]
echo URL=file:///%currentDir%start_systems.bat > "%desktop%\患者情報共有システム起動.url"

echo ショートカットを作成しました！
echo デスクトップの「患者情報共有システム起動」をダブルクリックしてください。
pause
