#!/bin/bash
# Auto-generated script to build executable for Employee_Engagement_Pulse

echo "=== Building Executable for Employee_Engagement_Pulse ==="
echo "Target file: /home/jyuc/Buildathon/projects/Employee_Engagement_Pulse/src/combined_final_output.py"

# Ensure dependencies are installed
echo "Installing dependencies..."
pip install -r "/home/jyuc/Buildathon/projects/Employee_Engagement_Pulse/requirements.txt"
pip install pyinstaller

# Create the executable with PyInstaller
echo "Building executable with PyInstaller..."
pyinstaller --onefile "/home/jyuc/Buildathon/projects/Employee_Engagement_Pulse/src/combined_final_output.py" --name "employee_engagement_pulse"

echo "=== Build Complete ==="
echo "Executable location: dist/employee_engagement_pulse"
echo "Run with: ./dist/employee_engagement_pulse"
