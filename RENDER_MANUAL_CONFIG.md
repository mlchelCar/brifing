# 🔧 Manual Render Configuration Guide

## ⚠️ If render.yaml is not being read, configure manually:

### 📱 **Telegram Bot Worker Service Configuration**

**Service Type**: Worker  
**Name**: `morningbrief-telegram-bot`  
**Environment**: Python 3  
**Runtime**: `python-3.12.7`  
**Build Command**: `chmod +x build.sh && ./build.sh`  
**Start Command**: `python start_telegram_bot.py`  

### 🌐 **Web Service Configuration**

**Service Type**: Web Service  
**Name**: `morningbrief-web`  
**Environment**: Python 3  
**Runtime**: `python-3.12.7`  
**Build Command**: `chmod +x build.sh && ./build.sh`  
**Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`  

### 🗄️ **Database Configuration**

**Database Type**: PostgreSQL  
**Name**: `morningbrief-db`  
**Database Name**: `morningbrief`  
**User**: `morningbrief_user`  
**Plan**: Free  

### 🔑 **Environment Variables (for both services)**

**Required Variables:**
- `DATABASE_URL` → Connect to PostgreSQL database
- `TELEGRAM_BOT_TOKEN` → Your Telegram bot token
- `OPENAI_API_KEY` → Your OpenAI API key  
- `NEWS_API_KEY` → Your News API key

**Optional Variables:**
- `DEBUG` → `false`
- `ENVIRONMENT` → `production`
- `PYTHON_VERSION` → `3.12.0`

### 🚀 **Deployment Steps**

1. **Create PostgreSQL Database** first
2. **Create Web Service** with above configuration
3. **Create Worker Service** with above configuration  
4. **Set Environment Variables** for both services
5. **Connect DATABASE_URL** to the PostgreSQL database
6. **Deploy both services**

### ✅ **Success Indicators**

- Build completes successfully
- No "setup_telegram_bot.py" errors
- Services start with correct commands
- Database connections work
- Telegram bot responds to `/start`

### 🔍 **Troubleshooting**

If you still see `setup_telegram_bot.py` errors:
1. Check the **Start Command** in Render dashboard
2. Ensure it's set to `python start_telegram_bot.py` (for worker)
3. Ensure it's set to `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (for web)
4. Clear any cached configurations in Render
5. Redeploy the services
