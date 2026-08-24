import os
import logging
import asyncio
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database import init_db, get_setting, cleanup_old_items
from i18n import t
from handlers import start, add_search, list_searches, delete_search, button_callback, handle_message, handle_link
from scheduler import platform_scheduler_loop, telegram_notifier_loop

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

global_loop = None
global_queue = None

async def cleanup_loop():
    logger.info("Database cleanup worker started.")
    while True:
        try:
            await asyncio.to_thread(cleanup_old_items, 10)
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
        await asyncio.sleep(12 * 3600)  # Check twice a day

async def post_init(application: Application):
    global global_loop, global_queue
    global_loop = asyncio.get_running_loop()
    global_queue = asyncio.Queue()
    
    asyncio.create_task(telegram_notifier_loop(application, global_queue))
    asyncio.create_task(platform_scheduler_loop(global_queue, "wallapop"))
    asyncio.create_task(platform_scheduler_loop(global_queue, "vinted"))
    asyncio.create_task(cleanup_loop())
    
    # Send startup message
    allowed_chats = get_setting("allowed_chat_ids", "")
    if allowed_chats:
        chat_ids = [int(cid.strip("'\" ")) for cid in allowed_chats.split(',') if cid.strip()]
        for chat_id in chat_ids:
            try:
                region = get_setting("region", "es")
                await application.bot.send_message(
                    chat_id=chat_id, 
                    text=t("bot_started", region),
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
    application.add_handler(CommandHandler("link", handle_link))
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
