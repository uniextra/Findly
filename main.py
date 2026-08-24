import os
import logging
import asyncio
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database import init_db, get_setting
from handlers import start, add_search, list_searches, delete_search, button_callback, handle_message
from scheduler import scheduler_loop, telegram_notifier_loop

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    notification_queue = asyncio.Queue()
    
    # Start the telegram notifier worker
    asyncio.create_task(telegram_notifier_loop(application, notification_queue))
    
    # Start the scanners
    asyncio.create_task(scheduler_loop(application, notification_queue))
    
    # Send startup message
    allowed_chats = get_setting("allowed_chat_ids", "")
    if allowed_chats:
        chat_ids = [int(cid.strip("'\" ")) for cid in allowed_chats.split(',') if cid.strip()]
        for chat_id in chat_ids:
            try:
                await application.bot.send_message(
                    chat_id=chat_id, 
                    text="🚀 <b>Findly Bot iniciado correctamente.</b>\nMonitoreo web y notificaciones activos.",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to send startup message to {chat_id}: {e}")

def restart_bot():
    """Restart the entire application to apply new settings"""
    logger.info("Restarting Findly...")
    os.execv(sys.executable, ['python', 'main.py'])

def main():
    # Initialize Database
    init_db()
    
    token = get_setting("telegram_token", "")
    if not token:
        logger.error("TELEGRAM_TOKEN not found in Settings or Env! Bot will not start. Please configure via Web UI.")
        # We don't return, we just block forever so web UI stays up
        import time
        while True:
            time.sleep(60)

    # Create Bot Application
    application = Application.builder().token(token).post_init(post_init).build()

    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_search))
    application.add_handler(CommandHandler("list", list_searches))
    application.add_handler(CommandHandler("delete", delete_search))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Handle text messages for direct URL adding
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start Bot
    logger.info("Starting Findly Bot...")
    application.run_polling()

if __name__ == "__main__":
    import threading
    import uvicorn
    
    def run_web():
        uvicorn.run("web:app", host="0.0.0.0", port=8000)
        
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    main()
