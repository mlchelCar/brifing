# Changelog

All notable changes to MorningBrief will be documented in this file.

## [2.0.0] - 2025-01-13

### 🎯 Strategic Changes
- **FOCUS ON FREE USERS**: Removed paid version from landing page to focus on free user acquisition
- **LICENSE CHANGE**: Migrated from proprietary license to MIT License for open source community
- **TELEGRAM BOT LINK**: Updated to real Telegram bot link: http://t.me/morn1ngbr1efbot

### ✨ Major Features Added
- **PERSONALIZED BRIEFINGS**: Complete personalization system with user names in greetings
- **SCHEDULED DELIVERY**: Per-user scheduled briefings with individual delivery times
- **TIME-BASED GREETINGS**: Dynamic greetings based on time of day (morning/afternoon/evening)
- **ENHANCED LOGGING**: Detailed delivery logs with user information and timestamps

### 🔧 Technical Improvements
- **Per-User Scheduling**: Individual CronTrigger jobs for each user's delivery time
- **Schedule Management**: Add/remove/update user schedules dynamically
- **Automatic Sync**: User schedules sync automatically on bot startup
- **Enhanced Bot Service**: Improved telegram bot service with personalization features

### 🎨 Landing Page Updates
- **Removed Pricing Section**: Eliminated Pro plan ($9/month) and pricing complexity
- **Updated CTAs**: Changed to "Start Free on Telegram" with emphasis on free service
- **Simplified Navigation**: Removed pricing links, added "Get Started Free" button
- **Free-First Messaging**: Updated all messaging to emphasize free value proposition
- **Real Bot Link**: Updated all links to actual Telegram bot

### 📝 License & Documentation
- **MIT License**: Switched to MIT License for open source distribution
- **Updated Copyright**: Removed proprietary notices from all source files
- **Improved Documentation**: Updated README with new bot link and features
- **Environment Setup**: Improved .env.example with proper placeholder values

### 🐛 Bug Fixes
- **Indentation Error**: Fixed critical IndentationError in start_telegram_bot.py
- **Event Loop Conflicts**: Resolved async event loop issues in bot startup
- **Schedule Conflicts**: Fixed user schedule management and job conflicts

### 🚀 Deployment Improvements
- **Python 3.13 Compatibility**: Full compatibility with Python 3.13.4
- **Render Deployment**: Optimized for Render cloud platform deployment
- **Database Connectivity**: Improved PostgreSQL connection handling
- **Error Handling**: Enhanced error handling and logging throughout

## [1.0.0] - 2025-01-10

### 🎉 Initial Release
- **Telegram Bot**: Basic news briefing bot with category selection
- **AI Summarization**: OpenAI GPT-4o-mini powered news summarization
- **News API Integration**: Real-time news fetching from NewsAPI.org
- **Database Support**: SQLite and PostgreSQL database support
- **Scheduler**: Automated daily news refresh and briefing delivery
- **Web Interface**: FastAPI web service with health monitoring
- **Landing Page**: Professional landing page with pricing tiers
