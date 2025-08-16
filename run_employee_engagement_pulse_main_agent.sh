#!/bin/bash
# Auto-generated script for project: Employee_Engagement_Pulse

echo "🚀 Starting main.py multi-agent system for project: Employee_Engagement_Pulse"
echo "📁 Project output directory: /home/jyuc/Buildathon/projects"
echo "🔧 Multi-agent path: /home/jyuc/Buildathon/multi_agent"
echo "🎯 Project: Employee_Engagement_Pulse"
echo "📝 Description: Employee Engagement Pulse Description: Provide managers with a weekly sentiment dashboard built from..."
echo "============================================================"

# Set environment variables for project processing
export PROJECT_OUTPUT_DIR="/home/jyuc/Buildathon/projects"
export PROJECT_NAME="Employee_Engagement_Pulse"

# Change to the multi-agent directory
cd "/home/jyuc/Buildathon/multi_agent"

# Create a temporary CSV file with just this project using Python for proper escaping
python3 << 'PYTHON_CSV_EOF'
import csv
import sys

# Project data
project_name = "Employee_Engagement_Pulse"
project_prompt = """Employee Engagement Pulse Description: Provide managers with a weekly sentiment dashboard built from all messages in configurable Slack channels. Requirements: • Monitor a user-defined list of Slack channels (include threads + reactions) • Run text & emoji sentiment analysis on every message • Aggregate daily mood into weekly trends with burnout warnings • Generate actionable, team-level insights for managers"""

# Write to CSV file with proper escaping
with open("temp_project_2.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["project_name", "prompt"])
    writer.writerow([project_name, project_prompt])

print(f"✅ Created temp CSV for project: {project_name}")
PYTHON_CSV_EOF

# Create a simple Python script to run the single project
cat > run_single_project.py << 'PYTHON_EOF'
import sys
import os
import csv

# Import the main processing functions
sys.path.insert(0, os.getcwd())
from main import process_single_project

def run_single_project_from_csv(csv_file):
    """Run a single project from a CSV file."""
    with open(csv_file, newline="", encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            project_name = row["project_name"]
            project_prompt = row["prompt"]
            
            print(f"\n🚀 Processing project: {project_name}")
            print(f"📝 Description: {project_prompt[:200]}...")
            
            try:
                result = process_single_project(project_name, project_prompt, 0, 1)
                if result['status'] == 'completed':
                    print(f"\n✅ Project completed successfully!")
                    print(f"📁 Project folder: {result.get('project_folder', 'Unknown')}")
                else:
                    print(f"\n❌ Project failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"\n💥 Error processing project: {e}")
                import traceback
                traceback.print_exc()
            break  # Process only the first (and only) project

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "temp_project_2.csv"
    run_single_project_from_csv(csv_file)
PYTHON_EOF

# Run the single project processor
python3 run_single_project.py "temp_project_2.csv"

# Clean up temporary files
rm -f "temp_project_2.csv" run_single_project.py

echo "============================================================"
echo "✅ Completed processing for project: Employee_Engagement_Pulse"
echo "📁 Check the project folder created by main.py"
echo "📊 Review the generated files for detailed results"
read -p "Press Enter to close this terminal..."
