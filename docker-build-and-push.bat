@echo off
REM Docker Build and Push Script for Windows
REM This script builds images and pushes them to Docker Hub

echo =====================================
echo AI Land Optimization - Docker Build
echo =====================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Get Docker Hub username
set /p DOCKER_USERNAME="Enter your Docker Hub username: "

if "%DOCKER_USERNAME%"=="" (
    echo Error: Docker Hub username cannot be empty
    exit /b 1
)

REM Version tag
set /p VERSION="Enter version tag (default: latest): "
if "%VERSION%"=="" set VERSION=latest

REM Login to Docker Hub
echo.
echo Logging in to Docker Hub...
docker login

if %errorlevel% neq 0 (
    echo Docker login failed. Exiting.
    exit /b 1
)

REM Build backend
echo.
echo Building backend image...
cd backend
docker build -t ai-land-optimization-backend:%VERSION% .
if %errorlevel% neq 0 (
    echo Backend build failed
    exit /b 1
)
echo Backend build successful!
cd ..

REM Build frontend
echo.
echo Building frontend image...
cd frontend
docker build -t ai-land-optimization-frontend:%VERSION% .
if %errorlevel% neq 0 (
    echo Frontend build failed
    exit /b 1
)
echo Frontend build successful!
cd ..

REM Tag images
echo.
echo Tagging images...
docker tag ai-land-optimization-backend:%VERSION% %DOCKER_USERNAME%/ai-land-optimization-backend:%VERSION%
docker tag ai-land-optimization-frontend:%VERSION% %DOCKER_USERNAME%/ai-land-optimization-frontend:%VERSION%

if not "%VERSION%"=="latest" (
    docker tag ai-land-optimization-backend:%VERSION% %DOCKER_USERNAME%/ai-land-optimization-backend:latest
    docker tag ai-land-optimization-frontend:%VERSION% %DOCKER_USERNAME%/ai-land-optimization-frontend:latest
)

REM Push images
echo.
echo Pushing backend to Docker Hub...
docker push %DOCKER_USERNAME%/ai-land-optimization-backend:%VERSION%
if not "%VERSION%"=="latest" (
    docker push %DOCKER_USERNAME%/ai-land-optimization-backend:latest
)

echo.
echo Pushing frontend to Docker Hub...
docker push %DOCKER_USERNAME%/ai-land-optimization-frontend:%VERSION%
if not "%VERSION%"=="latest" (
    docker push %DOCKER_USERNAME%/ai-land-optimization-frontend:latest
)

REM Summary
echo.
echo =====================================
echo Build and push completed!
echo =====================================
echo.
echo Images pushed:
echo   %DOCKER_USERNAME%/ai-land-optimization-backend:%VERSION%
echo   %DOCKER_USERNAME%/ai-land-optimization-frontend:%VERSION%

if not "%VERSION%"=="latest" (
    echo   %DOCKER_USERNAME%/ai-land-optimization-backend:latest
    echo   %DOCKER_USERNAME%/ai-land-optimization-frontend:latest
)

echo.
echo To run on Mac:
echo 1. Create docker-compose.yml with your username
echo 2. Run: docker-compose up -d
echo.
echo See DOCKER_SETUP.md for detailed instructions.

pause
