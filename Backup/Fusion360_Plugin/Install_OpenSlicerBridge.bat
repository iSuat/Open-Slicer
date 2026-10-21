@echo off
chcp 65001 >nul
echo ========================================================
echo   OpenSlicer Studio - Autodesk Fusion 360 Bridge Installer
echo ========================================================
set "SRC_DIR=%~dp0OpenSlicerBridge"
set "DEST_DIR=%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\OpenSlicerBridge"

if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"
xcopy /Y /E "%SRC_DIR%\*" "%DEST_DIR%\" >nul

echo.
echo [OK] OpenSlicerBridge Add-In basariyla kuruldu:
echo      %DEST_DIR%
echo.
echo Kullanim:
echo 1. Fusion 360 icinde UTILITIES -^> ADD-INS (Shift+S) acin.
echo 2. "OpenSlicerBridge" secip "Run" (ve "Run on Startup") isaretleyin.
echo 3. SOLID -^> MAKE altindaki "Send to OpenSlicer (Live STL)" butonuna basin
echo    veya tasarimi kaydettiginizde (Ctrl+S) otomatik guncellenir!
echo 4. SlicerStudio.html sol menude "Live Watch" butonuyla OpenSlicer_Live.stl secin.
echo.
pause
