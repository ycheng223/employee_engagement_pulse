@echo off
REM Docker build script for Employee_Engagement_Pulse

echo === Building Docker Image for Employee_Engagement_Pulse ===
docker build -t employee_engagement_pulse .

echo === Build Complete ===
echo Run the container with: docker_run.bat
