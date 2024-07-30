@echo off
setlocal

:: Set variables
set "url=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
set "zipfile=ffmpeg-master-latest-win64-gpl.zip"
set "tempdir=%~dp0temp_ffmpeg"
set "ffmpegdir=C:\ffmpeg"

:: Create a temporary directory
if exist "%tempdir%" rd /s /q "%tempdir%"
mkdir "%tempdir%"
cd /d "%tempdir%"

:: Download the zip file
echo Downloading FFmpeg...
powershell -Command "Invoke-WebRequest -Uri %url% -OutFile %zipfile%"

:: Extract the zip file
echo Extracting FFmpeg...
powershell -Command "Expand-Archive -Path %zipfile% -DestinationPath ."

:: Rename the extracted folder to 'ffmpeg'
for /d %%i in ("%tempdir%\*") do (
    if exist "%%i\bin\ffmpeg.exe" (
        ren "%%i" "ffmpeg"
        move "ffmpeg" "%ffmpegdir%"
    )
)

:: Add ffmpeg to system PATH
echo Setting PATH...
setx /m PATH "C:\ffmpeg\bin;%PATH%"

:: Cleanup
echo Cleaning up...
del "%zipfile%"
rd /s /q "%tempdir%"

echo FFmpeg installation and setup complete.
pause
endlocal

