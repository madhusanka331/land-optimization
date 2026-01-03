#!/bin/bash

# Docker Build and Push Script for AI Land Optimization System
# This script builds images and pushes them to Docker Hub

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}AI Land Optimization - Docker Build${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Get Docker Hub username
read -p "Enter your Docker Hub username: " DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${RED}Error: Docker Hub username cannot be empty${NC}"
    exit 1
fi

# Version tag
read -p "Enter version tag (default: latest): " VERSION
VERSION=${VERSION:-latest}

# Login to Docker Hub
echo -e "\n${BLUE}Logging in to Docker Hub...${NC}"
docker login

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker login failed. Exiting.${NC}"
    exit 1
fi

# Build backend
echo -e "\n${BLUE}Building backend image...${NC}"
cd backend
docker build -t ai-land-optimization-backend:${VERSION} .
if [ $? -ne 0 ]; then
    echo -e "${RED}Backend build failed${NC}"
    exit 1
fi
echo -e "${GREEN}Backend build successful!${NC}"
cd ..

# Build frontend
echo -e "\n${BLUE}Building frontend image...${NC}"
cd frontend
docker build -t ai-land-optimization-frontend:${VERSION} .
if [ $? -ne 0 ]; then
    echo -e "${RED}Frontend build failed${NC}"
    exit 1
fi
echo -e "${GREEN}Frontend build successful!${NC}"
cd ..

# Tag images
echo -e "\n${BLUE}Tagging images...${NC}"
docker tag ai-land-optimization-backend:${VERSION} ${DOCKER_USERNAME}/ai-land-optimization-backend:${VERSION}
docker tag ai-land-optimization-frontend:${VERSION} ${DOCKER_USERNAME}/ai-land-optimization-frontend:${VERSION}

if [ "$VERSION" != "latest" ]; then
    docker tag ai-land-optimization-backend:${VERSION} ${DOCKER_USERNAME}/ai-land-optimization-backend:latest
    docker tag ai-land-optimization-frontend:${VERSION} ${DOCKER_USERNAME}/ai-land-optimization-frontend:latest
fi

# Push images
echo -e "\n${BLUE}Pushing backend to Docker Hub...${NC}"
docker push ${DOCKER_USERNAME}/ai-land-optimization-backend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${DOCKER_USERNAME}/ai-land-optimization-backend:latest
fi

echo -e "\n${BLUE}Pushing frontend to Docker Hub...${NC}"
docker push ${DOCKER_USERNAME}/ai-land-optimization-frontend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${DOCKER_USERNAME}/ai-land-optimization-frontend:latest
fi

# Summary
echo -e "\n${GREEN}=====================================${NC}"
echo -e "${GREEN}Build and push completed!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "\nImages pushed:"
echo -e "  ${DOCKER_USERNAME}/ai-land-optimization-backend:${VERSION}"
echo -e "  ${DOCKER_USERNAME}/ai-land-optimization-frontend:${VERSION}"

if [ "$VERSION" != "latest" ]; then
    echo -e "  ${DOCKER_USERNAME}/ai-land-optimization-backend:latest"
    echo -e "  ${DOCKER_USERNAME}/ai-land-optimization-frontend:latest"
fi

echo -e "\n${BLUE}To run on Mac:${NC}"
echo -e "1. Create docker-compose.yml with your username"
echo -e "2. Run: docker-compose up -d"
echo -e "\nSee DOCKER_SETUP.md for detailed instructions."
