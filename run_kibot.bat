@echo off
setlocal

REM This script runs kibot using the Docker container on Windows
REM Usage: run_kibot.bat

REM Set the workspace directory (your project root)
set WORKSPACE_DIR=%CD%

REM Ensure Docker Desktop is running
where docker >nul
if %ERRORLEVEL% neq 0 (
    echo Error: Docker Desktop is not installed or not running.
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Define the Docker image
set DOCKER_IMAGE=ghcr.io/inti-cmnb/kicad9_auto:latest

REM Show what we're doing
echo ========================================
echo Running kibot Docker container...
echo Workspace: %WORKSPACE_DIR%
echo ========================================

REM Run kibot for left_pcb
echo.
echo ========================================
echo Processing: left_pcb
echo ========================================
echo Input PCB: ergogen/output/pcbs/left_pcb.kicad_pcb
echo Config: kibot/default.kibot.yaml
echo.
docker run --rm -v "%WORKSPACE_DIR%:/workdir" -w "/workdir" %DOCKER_IMAGE% bash -c "kibot -b ergogen/output/pcbs/left_pcb.kicad_pcb -c kibot/default.kibot.yaml"

REM Run kibot for right_pcb
echo.
echo ========================================
echo Processing: right_pcb
echo ========================================
echo Input PCB: ergogen/output/pcbs/right_pcb.kicad_pcb
echo Config: kibot/default.kibot.yaml
echo.
docker run --rm -v "%WORKSPACE_DIR%:/workdir" -w "/workdir" %DOCKER_IMAGE% bash -c "kibot -b ergogen/output/pcbs/right_pcb.kicad_pcb -c kibot/default.kibot.yaml"

echo.
echo ========================================
echo Done.
echo ========================================

endlocal
pause
