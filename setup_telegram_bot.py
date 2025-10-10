#!/usr/bin/env python3
"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car. All rights reserved.

REDIRECT SCRIPT: This script redirects to the correct startup process.
Render was trying to run this file due to cached configuration.
"""

import os
import sys
import subprocess

def main():
    print("🔄 REDIRECT: setup_telegram_bot.py is deprecated")
    print("🚀 Starting correct Telegram bot process...")
    
    # Check if this is being run as the main process
    if os.getenv('RENDER_SERVICE_TYPE') == 'worker':
        print("📱 Running Telegram bot worker service...")
        # Run the correct start script
        subprocess.run([sys.executable, "start_telegram_bot.py"])
    else:
        print("🌐 Running web service...")
        # Run the web service
        port = os.getenv('PORT', '8000')
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", port
        ])

if __name__ == "__main__":
    main()
