"""Script to run the Streamlit frontend."""

import subprocess
import sys
import os

def run_streamlit():
    """Run the Streamlit frontend application."""
    
    print("🚀 Starting Daily Briefing Frontend...")
    print("   Frontend URL: http://localhost:8501")
    print("   Make sure the backend is running on http://localhost:8000")
    print("   Press Ctrl+C to stop the frontend")
    print("-" * 50)
    
    # Get the path to the frontend app
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", frontend_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped.")
    except Exception as e:
        print(f"❌ Error running frontend: {e}")

if __name__ == "__main__":
    run_streamlit()
