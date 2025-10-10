"""Telegram webhook routes."""

import logging
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from app.config import settings
from app.services.telegram_bot import telegram_bot_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None)
):
    """Handle Telegram webhook updates."""
    try:
        # Verify webhook secret if configured
        if settings.TELEGRAM_WEBHOOK_SECRET:
            if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
                logger.warning("Invalid webhook secret token")
                raise HTTPException(status_code=403, detail="Invalid secret token")
        
        # Get update data
        update_data = await request.json()
        
        # Process update if bot is initialized
        if telegram_bot_service.application:
            from telegram import Update
            update = Update.de_json(update_data, telegram_bot_service.application.bot)
            await telegram_bot_service.application.process_update(update)
        else:
            logger.warning("Telegram bot not initialized, ignoring webhook")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/webhook/info")
async def webhook_info():
    """Get webhook information."""
    if not telegram_bot_service.application:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    try:
        webhook_info = await telegram_bot_service.application.bot.get_webhook_info()
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook info")

@router.post("/webhook/set")
async def set_webhook(webhook_url: str, secret_token: Optional[str] = None):
    """Set webhook URL for the bot."""
    if not telegram_bot_service.application:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    try:
        success = await telegram_bot_service.application.bot.set_webhook(
            url=webhook_url,
            secret_token=secret_token
        )
        
        if success:
            return {"status": "success", "message": "Webhook set successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to set webhook")
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to set webhook")

@router.delete("/webhook")
async def delete_webhook():
    """Delete webhook for the bot."""
    if not telegram_bot_service.application:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    try:
        success = await telegram_bot_service.application.bot.delete_webhook()
        
        if success:
            return {"status": "success", "message": "Webhook deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete webhook")
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook")

@router.get("/bot/info")
async def bot_info():
    """Get bot information."""
    if not telegram_bot_service.application:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    try:
        bot = telegram_bot_service.application.bot
        me = await bot.get_me()
        
        return {
            "id": me.id,
            "username": me.username,
            "first_name": me.first_name,
            "is_bot": me.is_bot,
            "can_join_groups": me.can_join_groups,
            "can_read_all_group_messages": me.can_read_all_group_messages,
            "supports_inline_queries": me.supports_inline_queries
        }
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bot info")

@router.post("/broadcast")
async def broadcast_message(message: str, parse_mode: Optional[str] = None):
    """Broadcast a message to all active users."""
    if not telegram_bot_service.application:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    try:
        from app.database import get_async_session
        from app.models import TelegramUser
        from sqlalchemy import select
        
        sent_count = 0
        failed_count = 0
        
        async with get_async_session() as session:
            result = await session.execute(
                select(TelegramUser).where(TelegramUser.is_active == True)
            )
            users = result.scalars().all()
            
            for user in users:
                try:
                    await telegram_bot_service.application.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message,
                        parse_mode=parse_mode
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send message to user {user.telegram_id}: {e}")
                    failed_count += 1
        
        return {
            "status": "success",
            "sent": sent_count,
            "failed": failed_count,
            "total": sent_count + failed_count
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")
