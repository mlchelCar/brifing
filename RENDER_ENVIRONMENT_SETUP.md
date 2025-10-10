# 🔑 Render Environment Variables Setup Guide

## 🎉 **GREAT NEWS: Your Application is Starting Successfully!**

The logs show your MorningBrief application is now working correctly:
- ✅ **Build successful** - All Python 3.13 compatibility issues resolved
- ✅ **Redirect script working** - Correct process detection
- ✅ **Graceful fallbacks** - SQLite working when PostgreSQL unavailable
- ❌ **Missing environment variables** - Need to set API keys and database URL

## 🔧 **Required Environment Variables**

You need to set these environment variables in your Render dashboard:

### **🤖 Telegram Bot Configuration**
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```
**How to get**: 
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Copy the token provided

### **🧠 OpenAI API Configuration**
```
OPENAI_API_KEY=sk-your_openai_api_key_here
```
**How to get**:
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

### **📰 News API Configuration**
```
NEWS_API_KEY=your_news_api_key_here
```
**How to get**:
1. Go to https://newsapi.org/register
2. Sign up for a free account
3. Copy your API key from the dashboard

### **🗄️ Database Configuration**
```
DATABASE_URL=postgresql://username:password@host:port/database
```
**How to get**: This is automatically provided when you connect your PostgreSQL database to your service in Render.

## 📋 **Step-by-Step Setup in Render Dashboard**

### **1. Set Environment Variables for Web Service**
1. Go to your Render dashboard
2. Click on your **morningbrief-web** service
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Add each variable:
   - `TELEGRAM_BOT_TOKEN` → Your bot token
   - `OPENAI_API_KEY` → Your OpenAI key  
   - `NEWS_API_KEY` → Your News API key
   - `DEBUG` → `false`
   - `ENVIRONMENT` → `production`

### **2. Set Environment Variables for Worker Service**
1. Click on your **morningbrief-telegram-bot** service
2. Go to **Environment** tab
3. Add the same variables as above

### **3. Connect Database**
1. Make sure your PostgreSQL database is created
2. In each service, add:
   - `DATABASE_URL` → Connect to your PostgreSQL database
3. Render will automatically provide the connection string

### **4. Deploy Services**
1. After setting all environment variables
2. Click **Manual Deploy** on both services
3. Monitor the logs for successful startup

## ✅ **Success Indicators**

After setting environment variables, you should see:
```
✅ All required environment variables are set
📊 Initializing database...
✅ Database initialized successfully
🤖 Starting Telegram bot...
✅ Telegram bot started successfully
```

## 🔍 **Testing Your Setup**

### **Test Telegram Bot**
1. Find your bot on Telegram (search for the name you gave it)
2. Send `/start` command
3. You should get a welcome message
4. Try `/briefing` to get a news summary

### **Test Web Interface**
1. Visit your Render web service URL
2. You should see the MorningBrief landing page
3. The health check endpoint should work

## 🚨 **Troubleshooting**

### **If you see "Missing required environment variables"**
- Double-check all environment variables are set in Render dashboard
- Make sure there are no extra spaces in the variable names or values
- Redeploy the service after adding variables

### **If Telegram bot doesn't respond**
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Check the bot is not running elsewhere
- Look for error messages in the worker service logs

### **If news summaries don't work**
- Verify `OPENAI_API_KEY` and `NEWS_API_KEY` are correct
- Check you have credits/quota available on both services
- Monitor the logs for API error messages

## 🎯 **Next Steps After Setup**

1. **Set environment variables** in Render dashboard
2. **Redeploy both services** (web and worker)
3. **Test the Telegram bot** with `/start` and `/briefing`
4. **Share your bot** with users!

## 💡 **Pro Tips**

- **Keep your API keys secure** - Never commit them to code
- **Monitor your usage** - Check OpenAI and News API quotas
- **Test regularly** - Make sure the bot responds correctly
- **Check logs** - Monitor Render service logs for any issues

**Your MorningBrief application is ready to go live! Just add the environment variables and you're all set!** 🚀
