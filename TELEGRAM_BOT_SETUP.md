# 🤖 MorningBrief Telegram Bot Setup Guide

This guide will help you set up and configure the MorningBrief Telegram bot.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Telegram account**
3. **API Keys**:
   - OpenAI API key
   - News API key
   - Telegram Bot Token

## 🚀 Quick Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "MorningBrief")
4. Choose a username (e.g., "MorningBriefBot")
5. Copy the bot token provided by BotFather

### Step 2: Configure Environment

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your credentials:**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   NEWS_API_KEY=your_news_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

### Step 3: Install Dependencies

```bash
# Option 1: Use the install script
python install_telegram_deps.py

# Option 2: Manual installation
pip install -r requirements.txt
```

### Step 4: Setup the Bot

```bash
python setup_telegram_bot.py
```

This will:
- Initialize the database
- Configure the bot
- Set up commands
- Test the connection

### Step 5: Start the Bot

```bash
python run_telegram_bot.py
```

## 🎯 Testing Your Bot

1. **Open Telegram**
2. **Search for your bot** using the username you created
3. **Send `/start`** to begin
4. **Follow the setup process**:
   - Select news categories
   - Choose delivery time
   - Test with `/briefing`

## 🔧 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start using MorningBrief |
| `/categories` | Select news categories |
| `/briefing` | Get your daily briefing now |
| `/settings` | Manage preferences |
| `/help` | Show help information |
| `/stop` | Stop receiving briefings |

## 📱 User Experience Flow

### 1. First Time Setup
```
User: /start
Bot: Welcome! Let's select your news categories...
User: [Selects categories via buttons]
Bot: Great! When would you like your daily briefing?
User: [Selects time via buttons]
Bot: Perfect! Setup complete!
```

### 2. Daily Usage
```
User: /briefing
Bot: 📰 Generating your briefing...
Bot: [Sends formatted news summary]
```

### 3. Settings Management
```
User: /settings
Bot: [Shows settings menu with buttons]
User: [Modifies categories/time/etc.]
Bot: Settings updated!
```

## 🌐 Production Deployment

### Option 1: Polling (Recommended for Development)
The bot runs continuously and polls Telegram for updates.

```bash
python run_telegram_bot.py
```

### Option 2: Webhooks (Recommended for Production)

1. **Deploy your app to a server** (Heroku, DigitalOcean, etc.)

2. **Set webhook URL in `.env`:**
   ```env
   TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram/webhook
   TELEGRAM_WEBHOOK_SECRET=your_secret_here
   ```

3. **Start the FastAPI server:**
   ```bash
   python run_backend.py
   ```

4. **Set the webhook:**
   ```bash
   curl -X POST "http://localhost:8000/telegram/webhook/set" \
        -H "Content-Type: application/json" \
        -d '{"webhook_url": "https://your-domain.com/telegram/webhook"}'
   ```

## 🔍 Monitoring and Management

### Check Bot Status
```bash
curl http://localhost:8000/telegram/bot/info
```

### View Webhook Info
```bash
curl http://localhost:8000/telegram/webhook/info
```

### Broadcast Message to All Users
```bash
curl -X POST "http://localhost:8000/telegram/broadcast" \
     -H "Content-Type: application/json" \
     -d '{"message": "📢 Important announcement!"}'
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Bot not initialized" error**
   - Check your `TELEGRAM_BOT_TOKEN` in `.env`
   - Verify the token with BotFather
   - Ensure no extra spaces in the token

2. **"Invalid configuration" error**
   - Verify all required environment variables are set
   - Check API key formats
   - Ensure `.env` file is in the project root

3. **Database errors**
   - Run `python setup_telegram_bot.py` again
   - Check file permissions
   - Ensure SQLite is available

4. **News not updating**
   - Verify `NEWS_API_KEY` is valid
   - Check internet connection
   - Review logs for API rate limits

### Debug Mode

Enable debug logging by setting:
```env
DEBUG=True
```

### Logs

Check the console output for detailed error messages and status updates.

## 📊 Database Schema

The bot creates these tables:
- `telegram_users` - User preferences and settings
- `news_articles` - Cached news articles

## 🔒 Security Considerations

1. **Keep your bot token secret**
2. **Use webhook secrets in production**
3. **Validate user inputs**
4. **Rate limit API calls**
5. **Monitor for abuse**

## 📈 Scaling

For high-volume usage:
1. Use webhooks instead of polling
2. Implement Redis for caching
3. Use PostgreSQL instead of SQLite
4. Add load balancing
5. Monitor performance metrics

## 🆘 Support

If you encounter issues:
1. Check this documentation
2. Review the logs
3. Test with a fresh bot token
4. Verify all dependencies are installed
5. Check the GitHub issues page
