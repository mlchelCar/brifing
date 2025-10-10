"""Install Telegram bot dependencies."""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies for Telegram bot."""
    print("📦 Installing Telegram bot dependencies...")
    
    try:
        # Install python-telegram-bot
        print("Installing python-telegram-bot...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "python-telegram-bot==20.7"
        ])
        print("✅ python-telegram-bot installed successfully")
        
        # Install all requirements
        print("Installing all requirements...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All requirements installed successfully")
        
        print("\n🎉 Installation complete!")
        print("Next steps:")
        print("1. Set up your .env file with TELEGRAM_BOT_TOKEN")
        print("2. Run: python setup_telegram_bot.py")
        print("3. Run: python run_telegram_bot.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("Please try installing manually:")
        print("pip install python-telegram-bot==20.7")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    install_dependencies()
