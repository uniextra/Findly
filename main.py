import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from database import init_db
from handlers import start, add_search, list_searches, delete_search, button_callback
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

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN not found!")
        return

    # Initialize Database
    init_db()

    # Create Bot Application
    application = Application.builder().token(token).post_init(post_init).build()

    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_search))
    application.add_handler(CommandHandler("list", list_searches))
    application.add_handler(CommandHandler("delete", delete_search))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Handle text messages for direct URL adding
    from telegram.ext import MessageHandler, filters
    from handlers import handle_message
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
