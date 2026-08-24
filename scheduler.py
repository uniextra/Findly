import asyncio
import random
import logging
from telegram.ext import Application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal, Search, SeenItem
from wallapop import search_items
from vinted import search_vinted

logger = logging.getLogger(__name__)

async def telegram_notifier_loop(application: Application, queue: asyncio.Queue):
    """
    Worker task that reads from the queue and sends messages to Telegram.
    This decouples the scraping process from the Telegram API limits.
    """
    logger.info("Telegram notifier worker started.")
    while True:
        try:
            # message_data can be a dict: {'type': 'photo', 'chat_id': 123, 'photo': 'url', 'caption': '...', 'parse_mode': 'HTML'}
            # or {'type': 'message', 'chat_id': 123, 'text': '...', 'parse_mode': 'HTML'}
            message_data = await queue.get()
            
            msg_type = message_data.get('type')
            chat_id = message_data.get('chat_id')
            
            try:
                if msg_type == 'photo':
                    await application.bot.send_photo(
                        chat_id=chat_id,
                        photo=message_data.get('photo'),
                        caption=message_data.get('caption'),
                        parse_mode=message_data.get('parse_mode', 'HTML'),
                        reply_markup=message_data.get('reply_markup')
                    )
                elif msg_type == 'message':
                    await application.bot.send_message(
                        chat_id=chat_id,
                        text=message_data.get('text'),
                        parse_mode=message_data.get('parse_mode', 'HTML'),
                        reply_markup=message_data.get('reply_markup')
                    )
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}: {e}")
                
            # Prevent hitting Telegram rate limits (approx 30 msgs/sec limit, but we do 1 msg per 0.5s for safety)
            await asyncio.sleep(0.5)
            
            queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Unexpected error in telegram_notifier_loop: {e}")
            await asyncio.sleep(1)

async def check_updates(application: Application, queue: asyncio.Queue):
    """
    Check for new items for all searches.
    """
    logger.info("Checking for updates...")
    db = SessionLocal()
    try:
        searches = db.query(Search).all()
        for search in searches:
            try:
                items = []
                
                # Default to both if None or empty
                platform = search.platform or "both"
                
                if platform in ["wallapop", "both"]:
                    items.extend(search_items(search.keywords, search.min_price, search.max_price, search.distance_in_km))
                
                if platform in ["vinted", "both"]:
                    items.extend(search_vinted(search.keywords, search.min_price, search.max_price))
                
                new_items_count = 0
                max_items_to_notify = 10
                
                for item in items:
                    item_id = item["id"]
                    
                    # Check if already seen
                    exists = db.query(SeenItem).filter(SeenItem.wallapop_id == str(item_id), SeenItem.search_id == search.id).first()
                    if exists:
                        continue
                        
                    # New item found
                    new_items_count += 1
                    
                    # Mark as seen immediately to avoid re-processing
                    seen = SeenItem(wallapop_id=str(item_id), search_id=search.id)
                    db.add(seen)
                    db.commit()

                    if new_items_count <= max_items_to_notify:
                        logger.info(f"New item found for search {search.id}: {item['title']}")
                        
                        # Send notification via queue
                        plat_name = item.get('platform', 'Wallapop')
                        msg = (
                            f"🔔 <b>Nuevo artículo encontrado en {plat_name}!</b>\n\n"
                            f"<b>{item['title']}</b>\n"
                            f"💶 Precio: {int(item['price'])} {item['currency']}\n"
                            f"<a href='{item['url']}'>Ver en {plat_name}</a>"
                        )
                        
                        keyboard = [[InlineKeyboardButton("❌ Dejar de seguir", callback_data=f"delete_{search.id}")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        if item.get('image'):
                            await queue.put({
                                'type': 'photo',
                                'chat_id': search.chat_id,
                                'photo': item['image'],
                                'caption': msg,
                                'parse_mode': 'HTML',
                                'reply_markup': reply_markup
                            })
                        else:
                            await queue.put({
                                'type': 'message',
                                'chat_id': search.chat_id,
                                'text': msg,
                                'parse_mode': 'HTML',
                                'reply_markup': reply_markup
                            })
                
                if new_items_count > max_items_to_notify:
                    import urllib.parse
                    base_web_url = "https://es.wallapop.com/search"
                    params = {
                        "keywords": search.keywords,
                        "latitude": 41.4231,
                        "longitude": 2.188,
                        "order_by": "newest",
                        "country_code": "ES",
                        "source": "search_box",
                        "time_filter": "today"
                    }
                    if search.distance_in_km:
                        params["distance_in_km"] = search.distance_in_km
                    if search.min_price:
                        params["min_sale_price"] = search.min_price
                    if search.max_price:
                        params["max_sale_price"] = search.max_price
                        
                    web_url = f"{base_web_url}?{urllib.parse.urlencode(params)}"
                    
                    summary_msg = (
                        f"⚠️ <b>Se han encontrado {new_items_count} artículos nuevos.</b>\n"
                        f"Solo se han mostrado los primeros {max_items_to_notify}.\n"
                    )
                    if platform == "wallapop":
                         summary_msg += f"<a href='{web_url}'>Ver todos los resultados en Wallapop</a>"
                    elif platform == "vinted":
                         summary_msg += f"<a href='https://www.vinted.es/catalog?search_text={search.keywords}'>Ver todos los resultados en Vinted</a>"
                    else:
                         summary_msg += f"<a href='{web_url}'>Ver en Wallapop</a> | <a href='https://www.vinted.es/catalog?search_text={search.keywords}'>Ver en Vinted</a>"
                         
                    keyboard = [[InlineKeyboardButton("❌ Dejar de seguir", callback_data=f"delete_{search.id}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                         
                    await queue.put({
                        'type': 'message',
                        'chat_id': search.chat_id,
                        'text': summary_msg,
                        'parse_mode': 'HTML',
                        'reply_markup': reply_markup
                    })
                        
            except Exception as e:
                logger.error(f"Error processing search {search.id}: {e}")
            
            # Wait 30 seconds between searches to avoid flooding the API
            await asyncio.sleep(30)
                
    finally:
        db.close()

async def scheduler_loop(application: Application, queue: asyncio.Queue):
    """
    Runs the check_updates function every 5 minutes +/- 2 minutes.
    """
    logger.info("Scheduler started. Performing initial check immediately...")
    while True:
        try:
            await check_updates(application, queue)
        except Exception as e:
            logger.error(f"Unexpected error in check_updates: {e}")
            
        wait_time = 300 + random.uniform(-120, 120)
        logger.info(f"Next check in {wait_time:.2f} seconds")
        await asyncio.sleep(wait_time)


