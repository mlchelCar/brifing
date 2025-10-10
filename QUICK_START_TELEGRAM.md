# 🚀 MorningBrief Telegram Bot - Quick Start

## ⚡ 3-Minute Setup

### 1. Get Your Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Choose name: `MorningBrief`
4. Choose username: `YourNameMorningBriefBot`
5. Copy the token

### 2. Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env file and add:
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
NEWS_API_KEY=your_news_api_key_here
```

### 3. Install & Setup
```bash
# Install dependencies
python install_telegram_deps.py

# Setup bot
python setup_telegram_bot.py

# Start bot
python run_telegram_bot.py
```

### 4. Test Your Bot
1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. Follow the setup flow
5. Test with `/briefing`

## 🤖 Bot Commands

| Command | What it does |
|---------|-------------|
| `/start` | Welcome & setup |
| `/categories` | Choose news topics |
| `/briefing` | Get news now |
| `/settings` | Change preferences |
| `/help` | Show help |
| `/stop` | Unsubscribe |

## 📱 User Experience

```
👤 User: /start
🤖 Bot: Welcome! Let's select your news categories...
     [Technology] [Business] [Sports] [World]
     
👤 User: [Clicks Technology, Business]
🤖 Bot: Great! When would you like your daily briefing?
     [06:00] [07:00] [08:00] [09:00]
     
👤 User: [Clicks 07:00]
🤖 Bot: Perfect! Setup complete! 
     • Get briefing now: /briefing
     • Change settings: /settings

👤 User: /briefing
🤖 Bot: 📰 Your Morning Brief
     
     Technology
     • Breakthrough in quantum computing shows 1000x speed...
     • New smartphone features announced at tech conference...
     
     Business  
     • Major merger announced between Fortune 500 companies...
     • Stock market reaches new highs amid positive earnings...
```

## 🔧 Troubleshooting

**Bot not responding?**
- Check your bot token in `.env`
- Verify the bot is running: `python run_telegram_bot.py`

**"Invalid configuration" error?**
- Ensure all API keys are in `.env`
- No extra spaces in the keys

**No news showing?**
- Check your News API key
- Verify internet connection

## 🌐 Production Deployment

For production, use webhooks instead of polling:

1. Deploy to server (Heroku, DigitalOcean, etc.)
2. Set webhook URL in `.env`:
   ```env
   TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram/webhook
   ```
3. Start with: `python run_backend.py`

## 📊 Features

✅ **User Management**
- Automatic registration
- Category preferences
- Custom delivery times
- Active/inactive status

✅ **News Curation**
- Multiple categories
- Smart summarization
- Daily scheduling
- On-demand requests

✅ **Bot Interface**
- Interactive keyboards
- Intuitive commands
- Error handling
- Help system

✅ **Production Ready**
- Webhook support
- Database storage
- Logging & monitoring
- Broadcast messaging

## 🎯 Next Steps

1. **Customize Categories**: Edit `AVAILABLE_CATEGORIES` in `app/config.py`
2. **Adjust Timing**: Modify scheduler settings
3. **Brand Your Bot**: Update messages in `app/services/telegram_bot.py`
4. **Add Features**: Extend with new commands
5. **Monitor Usage**: Check logs and user metrics

## 📚 Documentation

- **Full Setup**: `TELEGRAM_BOT_SETUP.md`
- **API Docs**: `http://localhost:8000/docs`
- **Project README**: `README.md`

---

**🎉 Your MorningBrief Telegram bot is ready to deliver curated news to users worldwide!**
