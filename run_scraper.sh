#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists (adjust path as needed for hosting)
# On BigRock/cPanel, you might need to use the full path to the python executable
# e.g., /home/username/virtualenv/path/to/bin/python

if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the extraction script
python3 extract_schedule.py

# Optional: Add logging
echo "Schedule updated at $(date)" >> scraper.log
