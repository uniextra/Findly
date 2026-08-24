import asyncio
import random
import logging
from datetime import datetime
from telegram.ext import Application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal, Search, SeenItem, get_setting
from i18n import t
from wallapop import search_items
from vinted import search_vinted
import urllib.parse

logger = logging.getLogger(__name__)

async def telegram_notifier_loop(application: Application, queue: asyncio.Queue):
    logger.info("Telegram notifier worker started.")
    while True:
        try:
            message_data = await queue.get()
            msg_type = message_data.get('type')
            
            from database import get_setting
            allowed_str = get_setting("allowed_chat_ids", "")
            try:
                chat_ids = [int(cid.strip("'\" ")) for cid in allowed_str.split(',') if cid.strip()]
            except:
                chat_ids = []
                
            for chat_id in chat_ids:
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
                
            await asyncio.sleep(0.5)
            queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Unexpected error in telegram_notifier_loop: {e}")
            await asyncio.sleep(1)

async def check_single_search(search_id: int, queue: asyncio.Queue, platform_override=None):
    """
    Check for new items for a single search.
    If platform_override is provided, only check that platform.
    """
    db = SessionLocal()
    try:
        search = db.query(Search).filter(Search.id == search_id).first()
        if not search:
            return
            
        logger.info(f"Checking updates for search {search.id}")
        items = []
        
        target_platform = platform_override or search.platform or "both"
        
        if target_platform in ["wallapop", "both"]:
            items.extend(search_items(search.keywords, search.min_price, search.max_price, search.distance_in_km))
        
        if target_platform in ["vinted", "both"]:
            items.extend(search_vinted(search.keywords, search.min_price, search.max_price))
        
        new_items_count = 0
        max_items_to_notify = 10
        
        for item in items:
            item_id = item["id"]
            exists = db.query(SeenItem).filter(SeenItem.wallapop_id == str(item_id), SeenItem.search_id == search.id).first()
            if exists:
                continue
                
            new_items_count += 1
            seen = SeenItem(
                wallapop_id=str(item_id), 
                search_id=search.id,
                title=item.get('title'),
                price=item.get('price'),
                url=item.get('url')
            )
            db.add(seen)
            db.commit()

            if new_items_count <= max_items_to_notify:
                plat_name = item.get('platform', 'Wallapop')
                msg = (
                    f"🎁 <b>Nuevo artículo encontrado en {plat_name}!</b>\n\n"
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
            region = get_setting("region", "es").lower()
            wallapop_region = region if region in ["es", "it", "pt"] else "es"
            vinted_domain = "co.uk" if region == "uk" else region
            
            base_web_url = f"https://{wallapop_region}.wallapop.com/search"
            params = {
                "keywords": search.keywords,
                "order_by": "newest",
                "time_filter": "today"
            }
            if search.min_price: params["min_sale_price"] = search.min_price
            if search.max_price: params["max_sale_price"] = search.max_price
                
            web_url = f"{base_web_url}?{urllib.parse.urlencode(params)}"
            vinted_url = f"https://www.vinted.{vinted_domain}/catalog?search_text={search.keywords}"
            
            summary_msg = t("new_items_found", region, count=new_items_count)
            summary_msg += t("showing_first", region, count=max_items_to_notify)
            
            if target_platform == "wallapop":
                 summary_msg += f"<a href='{web_url}'>{t('view_wallapop_all', region)}</a>"
            elif target_platform == "vinted":
                 summary_msg += f"<a href='{vinted_url}'>{t('view_vinted_all', region)}</a>"
            else:
                 summary_msg += f"<a href='{web_url}'>{t('view_wallapop', region)}</a> | <a href='{vinted_url}'>{t('view_vinted', region)}</a>"

                 
            keyboard = [[InlineKeyboardButton("❌ Dejar de seguir", callback_data=f"delete_{search.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
                 
            await queue.put({
                'type': 'message',
                'chat_id': search.chat_id,
                'text': summary_msg,
                'parse_mode': 'HTML',
                'reply_markup': reply_markup
            })
            
        search.last_checked_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        logger.error(f"Error processing search {search_id}: {e}")
    finally:
        db.close()


async def platform_scheduler_loop(queue: asyncio.Queue, platform: str):
    """
    Runs check for a specific platform based on its interval.
    """
    logger.info(f"Scheduler started for {platform}.")
    while True:
        try:
            interval_str = get_setting(f"{platform}_interval", "5")
            interval_mins = int(interval_str)
        except ValueError:
            interval_mins = 5
            
        db = SessionLocal()
        try:
            # Get searches that include this platform or 'both'
            searches = db.query(Search).filter(Search.platform.in_([platform, "both"])).all()
            for search in searches:
                await check_single_search(search.id, queue, platform_override=platform)
                await asyncio.sleep(15) # Wait 15s between each search to avoid flooding
        except Exception as e:
            logger.error(f"Unexpected error in {platform} scheduler: {e}")
        finally:
            db.close()
            
        # Add random jitter between -30s and +30s
        wait_time = (interval_mins * 60) + random.uniform(-30, 30)
        logger.info(f"Next check for {platform} in {wait_time/60:.1f} minutes")
        await asyncio.sleep(max(wait_time, 60)) # Ensure at least 60s
