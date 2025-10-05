@echo off
echo スタートメニューに追加中...

set "currentDir=%~dp0"
set "startMenu=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

echo [DesktopShortcut]
echo URL=file:///%currentDir%start_systems.bat
echo IconFile=%currentDir%start_systems.bat
echo IconIndex=0
echo HotKey=0
echo IDList=
echo [InternetShortcut]
echo URL=file:///%currentDir%start_systems.bat > "%startMenu%\患者情報共有システム起動.url"

echo スタートメニューに追加しました！
echo スタートボタンから「患者情報共有システム起動」を検索してクリックできます。
pause
