# 🚀 Render Deployment Guide for MorningBrief

This guide will help you deploy your MorningBrief application to Render with both the web interface and Telegram bot.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **API Keys**: Have your API keys ready:
   - Telegram Bot Token
   - OpenAI API Key
   - NewsAPI Key

## 🗄️ Step 1: Create PostgreSQL Database

1. Go to your Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `morningbrief-db`
   - **Database**: `morningbrief`
   - **User**: `morningbrief_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
4. Click **"Create Database"**
5. **Save the connection details** (you'll need the External Database URL)

## 🌐 Step 2: Deploy Web Service (Landing Page)

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `morningbrief-web`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for production)

### Environment Variables for Web Service:
```
DATABASE_URL=<your-postgresql-external-url>
OPENAI_API_KEY=<your-openai-api-key>
NEWS_API_KEY=<your-newsapi-key>
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
DEBUG=false
ENVIRONMENT=production
```

## 🤖 Step 3: Deploy Telegram Bot (Background Service)

1. Click **"New +"** → **"Background Worker"**
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `morningbrief-telegram-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_telegram_bot.py`
   - **Plan**: Free (or paid for production)

### Environment Variables for Bot Service:
```
DATABASE_URL=<your-postgresql-external-url>
OPENAI_API_KEY=<your-openai-api-key>
NEWS_API_KEY=<your-newsapi-key>
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
DEBUG=false
ENVIRONMENT=production
```

## 🔧 Step 4: Configure Environment Variables

For both services, add these environment variables:

### Required Variables:
- **`DATABASE_URL`**: PostgreSQL connection string from Step 1
- **`TELEGRAM_BOT_TOKEN`**: From @BotFather on Telegram
- **`OPENAI_API_KEY`**: From OpenAI dashboard
- **`NEWS_API_KEY`**: From newsapi.org

### Optional Variables:
- **`DEBUG`**: Set to `false` for production
- **`ENVIRONMENT`**: Set to `production`

## 📊 Step 5: Database Setup

The database will be automatically initialized when the Telegram bot starts. The startup script will:

1. Create all necessary tables
2. Set up the schema for users and articles
3. Start the bot service

## 🔍 Step 6: Verify Deployment

### Check Web Service:
1. Visit your web service URL (provided by Render)
2. You should see the MorningBrief landing page
3. Check the `/health` endpoint for API status

### Check Telegram Bot:
1. Go to your bot on Telegram
2. Send `/start` command
3. The bot should respond with the welcome message
4. Try `/briefing` command (may show "no articles" initially)

### Check Logs:
- Monitor both services in Render dashboard
- Look for successful startup messages
- Check for any error messages

## 🚨 Troubleshooting

### Common Issues:

1. **Database Connection Errors**:
   - Verify DATABASE_URL is correct
   - Check PostgreSQL service is running
   - Ensure asyncpg is installed

2. **Bot Not Responding**:
   - Verify TELEGRAM_BOT_TOKEN is correct
   - Check bot service logs
   - Ensure bot is not running elsewhere

3. **API Errors**:
   - Verify all API keys are set
   - Check API key permissions
   - Monitor rate limits

4. **Build Failures**:
   - Check requirements.txt is complete
   - Verify Python version compatibility
   - Check for missing dependencies

### Log Commands:
```bash
# View web service logs
render logs --service morningbrief-web

# View bot service logs  
render logs --service morningbrief-telegram-bot
```

## 📈 Step 7: Production Considerations

### Scaling:
- Upgrade to paid plans for better performance
- Consider multiple regions for global users
- Monitor resource usage

### Security:
- Use environment variables for all secrets
- Enable HTTPS (automatic on Render)
- Monitor access logs

### Monitoring:
- Set up health checks
- Monitor database performance
- Track bot usage metrics

## 🎉 Success!

Your MorningBrief application is now deployed on Render with:
- ✅ Landing page accessible via web
- ✅ Telegram bot running 24/7
- ✅ PostgreSQL database
- ✅ Automatic deployments from GitHub

## 📞 Support

If you encounter issues:
1. Check Render documentation
2. Review service logs
3. Verify environment variables
4. Test locally first

Your MorningBrief application is now ready to serve users worldwide! 🌍
