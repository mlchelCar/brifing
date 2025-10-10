"""Telegram bot service for MorningBrief."""

import asyncio
import logging
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.config import settings
from app.database import get_async_session
from app.models import TelegramUser, NewsArticle
from app.services.summarizer import summarizer_service

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Telegram bot service for MorningBrief."""
    
    def __init__(self):
        self.application: Optional[Application] = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize the Telegram bot."""
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not configured")
            return False
            
        try:
            # Create application
            self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            
            # Add handlers
            await self._setup_handlers()
            
            # Set bot commands
            await self._setup_commands()
            
            logger.info("Telegram bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            return False
    
    async def _setup_handlers(self):
        """Setup bot command and callback handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("categories", self._categories_command))
        self.application.add_handler(CommandHandler("briefing", self._briefing_command))
        self.application.add_handler(CommandHandler("settings", self._settings_command))
        self.application.add_handler(CommandHandler("stop", self._stop_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self._handle_category_selection, pattern="^cat_"))
        self.application.add_handler(CallbackQueryHandler(self._handle_time_selection, pattern="^time_"))
        self.application.add_handler(CallbackQueryHandler(self._handle_settings, pattern="^set_"))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    async def _setup_commands(self):
        """Setup bot commands menu."""
        commands = [
            BotCommand("start", "Start using MorningBrief"),
            BotCommand("categories", "Select news categories"),
            BotCommand("briefing", "Get your daily briefing now"),
            BotCommand("settings", "Manage your preferences"),
            BotCommand("help", "Show help information"),
            BotCommand("stop", "Stop receiving briefings")
        ]
        
        await self.application.bot.set_my_commands(commands)
    
    async def start_polling(self):
        """Start the bot with polling."""
        if not self.application:
            logger.error("Bot not initialized")
            return
            
        try:
            self.is_running = True
            logger.info("Starting Telegram bot polling...")
            await self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Stop the bot."""
        if self.application and self.is_running:
            logger.info("Stopping Telegram bot...")
            await self.application.stop()
            self.is_running = False
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Save or update user in database
        await self._save_user(user)
        
        welcome_text = (
            f"🌅 Welcome to MorningBrief, {user.first_name}!\n\n"
            "Get your daily news briefing delivered right here on Telegram. "
            "I'll curate the most important stories from your selected categories "
            "and deliver them in a concise, easy-to-read format.\n\n"
            "Let's get started by selecting your news categories:"
        )
        
        keyboard = await self._get_categories_keyboard()
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = (
            "🤖 *MorningBrief Help*\n\n"
            "*Available Commands:*\n"
            "/start - Start using MorningBrief\n"
            "/categories - Select your news categories\n"
            "/briefing - Get your daily briefing now\n"
            "/settings - Manage your preferences\n"
            "/help - Show this help message\n"
            "/stop - Stop receiving briefings\n\n"
            "*How it works:*\n"
            "1. Select your preferred news categories\n"
            "2. Choose when you want to receive your daily briefing\n"
            "3. Get curated news summaries delivered automatically\n\n"
            "*Need more help?* Contact our support team."
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _categories_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /categories command."""
        keyboard = await self._get_categories_keyboard()
        text = "📰 Select your news categories (you can choose multiple):"
        
        await update.message.reply_text(text, reply_markup=keyboard)
    
    async def _briefing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /briefing command."""
        user_id = update.effective_user.id
        
        # Get user's selected categories
        async with get_async_session() as session:
            result = await session.execute(
                select(TelegramUser).where(TelegramUser.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.selected_categories:
                await update.message.reply_text(
                    "❌ Please select your news categories first using /categories"
                )
                return
            
            # Generate briefing
            await update.message.reply_text("📰 Generating your briefing...")
            briefing = await self._generate_briefing(user.selected_categories)
            
            if briefing:
                await update.message.reply_text(briefing, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "❌ Sorry, I couldn't generate your briefing right now. Please try again later."
                )
    
    async def _settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📰 Change Categories", callback_data="set_categories")],
            [InlineKeyboardButton("⏰ Set Daily Time", callback_data="set_time")],
            [InlineKeyboardButton("🌍 Timezone", callback_data="set_timezone")],
            [InlineKeyboardButton("❌ Stop Briefings", callback_data="set_stop")]
        ])
        
        await update.message.reply_text(
            "⚙️ *Settings*\n\nWhat would you like to change?",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command."""
        user_id = update.effective_user.id
        
        async with get_async_session() as session:
            await session.execute(
                update(TelegramUser)
                .where(TelegramUser.telegram_id == user_id)
                .values(is_active=False)
            )
            await session.commit()
        
        await update.message.reply_text(
            "😢 You've been unsubscribed from MorningBrief.\n\n"
            "You can restart anytime by sending /start"
        )
    
    async def _handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category selection callbacks."""
        query = update.callback_query
        await query.answer()
        
        category = query.data.replace("cat_", "")
        user_id = update.effective_user.id
        
        # Toggle category selection
        async with get_async_session() as session:
            result = await session.execute(
                select(TelegramUser).where(TelegramUser.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                categories = user.selected_categories or []
                if category in categories:
                    categories.remove(category)
                else:
                    categories.append(category)
                
                await session.execute(
                    update(TelegramUser)
                    .where(TelegramUser.telegram_id == user_id)
                    .values(selected_categories=categories)
                )
                await session.commit()
                
                # Update keyboard
                keyboard = await self._get_categories_keyboard(selected=categories)
                await query.edit_message_reply_markup(reply_markup=keyboard)
                
                if categories:
                    await query.message.reply_text(
                        f"✅ Updated! Selected categories: {', '.join(categories)}\n\n"
                        "Now let's set when you want to receive your daily briefing:"
                    )
                    time_keyboard = await self._get_time_keyboard()
                    await query.message.reply_text(
                        "⏰ When would you like to receive your daily briefing?",
                        reply_markup=time_keyboard
                    )
    
    async def _handle_time_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle time selection callbacks."""
        query = update.callback_query
        await query.answer()
        
        time_str = query.data.replace("time_", "")
        user_id = update.effective_user.id
        
        async with get_async_session() as session:
            await session.execute(
                update(TelegramUser)
                .where(TelegramUser.telegram_id == user_id)
                .values(daily_time=time_str)
            )
            await session.commit()
        
        await query.edit_message_text(
            f"✅ Perfect! You'll receive your daily briefing at {time_str} UTC.\n\n"
            "🎉 Setup complete! You can:\n"
            "• Get your briefing now with /briefing\n"
            "• Change settings anytime with /settings\n"
            "• Get help with /help"
        )

    async def _handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings callbacks."""
        query = update.callback_query
        await query.answer()

        action = query.data.replace("set_", "")

        if action == "categories":
            keyboard = await self._get_categories_keyboard()
            await query.edit_message_text(
                "📰 Select your news categories:",
                reply_markup=keyboard
            )
        elif action == "time":
            keyboard = await self._get_time_keyboard()
            await query.edit_message_text(
                "⏰ When would you like to receive your daily briefing?",
                reply_markup=keyboard
            )
        elif action == "timezone":
            await query.edit_message_text(
                "🌍 Timezone settings coming soon! Currently using UTC."
            )
        elif action == "stop":
            user_id = update.effective_user.id
            async with get_async_session() as session:
                await session.execute(
                    update(TelegramUser)
                    .where(TelegramUser.telegram_id == user_id)
                    .values(is_active=False)
                )
                await session.commit()

            await query.edit_message_text(
                "😢 You've been unsubscribed from MorningBrief.\n\n"
                "You can restart anytime by sending /start"
            )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        await update.message.reply_text(
            "🤖 I understand commands better! Try:\n"
            "/briefing - Get your daily briefing\n"
            "/categories - Select news categories\n"
            "/help - Show all commands"
        )

    async def _save_user(self, user):
        """Save or update user in database."""
        async with get_async_session() as session:
            # Check if user exists
            result = await session.execute(
                select(TelegramUser).where(TelegramUser.telegram_id == user.id)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # Update existing user
                await session.execute(
                    update(TelegramUser)
                    .where(TelegramUser.telegram_id == user.id)
                    .values(
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code,
                        last_interaction=datetime.utcnow(),
                        is_active=True
                    )
                )
            else:
                # Create new user
                new_user = TelegramUser(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    language_code=user.language_code,
                    is_active=True,
                    last_interaction=datetime.utcnow()
                )
                session.add(new_user)

            await session.commit()

    async def _get_categories_keyboard(self, selected: List[str] = None) -> InlineKeyboardMarkup:
        """Generate categories selection keyboard."""
        if selected is None:
            selected = []

        categories = settings.AVAILABLE_CATEGORIES
        keyboard = []

        # Create rows of 2 buttons each
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    cat = categories[i + j]
                    emoji = "✅" if cat in selected else "📰"
                    text = f"{emoji} {cat.title()}"
                    row.append(InlineKeyboardButton(text, callback_data=f"cat_{cat}"))
            keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    async def _get_time_keyboard(self) -> InlineKeyboardMarkup:
        """Generate time selection keyboard."""
        times = ["06:00", "07:00", "08:00", "09:00", "10:00", "12:00", "18:00", "20:00"]
        keyboard = []

        # Create rows of 2 buttons each
        for i in range(0, len(times), 2):
            row = []
            for j in range(2):
                if i + j < len(times):
                    time_str = times[i + j]
                    row.append(InlineKeyboardButton(f"⏰ {time_str}", callback_data=f"time_{time_str}"))
            keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    async def _generate_briefing(self, categories: List[str]) -> Optional[str]:
        """Generate a briefing for the given categories."""
        try:
            async with get_async_session() as session:
                # Get recent articles for selected categories
                result = await session.execute(
                    select(NewsArticle)
                    .where(
                        NewsArticle.category.in_(categories),
                        NewsArticle.is_active == True,
                        NewsArticle.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    )
                    .order_by(NewsArticle.created_at.desc())
                    .limit(10)
                )
                articles = result.scalars().all()

                if not articles:
                    return "📰 No recent articles found for your selected categories. Try again later!"

                # Format briefing
                briefing = "🌅 *Your Morning Brief*\n\n"

                # Group articles by category
                by_category = {}
                for article in articles:
                    if article.category not in by_category:
                        by_category[article.category] = []
                    by_category[article.category].append(article)

                for category, cat_articles in by_category.items():
                    briefing += f"*{category.title()}*\n"
                    for article in cat_articles[:3]:  # Max 3 articles per category
                        summary = article.summary or article.description or "No summary available"
                        if len(summary) > 200:
                            summary = summary[:200] + "..."

                        briefing += f"• [{article.title}]({article.url})\n"
                        briefing += f"  {summary}\n\n"
                    briefing += "\n"

                briefing += f"📅 Generated at {datetime.utcnow().strftime('%H:%M UTC')}"
                return briefing

        except Exception as e:
            logger.error(f"Error generating briefing: {e}")
            return None

    async def send_daily_briefings(self):
        """Send daily briefings to all active users."""
        try:
            async with get_async_session() as session:
                # Get all active users
                result = await session.execute(
                    select(TelegramUser).where(TelegramUser.is_active == True)
                )
                users = result.scalars().all()

                for user in users:
                    if user.selected_categories and user.daily_time:
                        try:
                            briefing = await self._generate_briefing(user.selected_categories)
                            if briefing:
                                await self.application.bot.send_message(
                                    chat_id=user.telegram_id,
                                    text=briefing,
                                    parse_mode='Markdown'
                                )
                                logger.info(f"Sent briefing to user {user.telegram_id}")
                        except Exception as e:
                            logger.error(f"Failed to send briefing to user {user.telegram_id}: {e}")

        except Exception as e:
            logger.error(f"Error sending daily briefings: {e}")


# Global bot service instance
telegram_bot_service = TelegramBotService()
