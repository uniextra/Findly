from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database import SessionLocal, Search, get_setting
from i18n import t

def get_db_session():
    return SessionLocal()

import os
from functools import wraps

def restricted(func):
    """Decorator to restrict access to allowed user IDs."""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        allowed_chats_str = get_setting("allowed_chat_ids", "")
        
        # Parse the string into a list of integers, handling empty or invalid entries gracefully
        try:
            allowed_chats = [int(cid.strip("'\" ")) for cid in allowed_chats_str.split(',') if cid.strip()]
        except ValueError:
            allowed_chats = []
            
        chat_id = update.effective_chat.id
        
        if update.message and update.message.text:
            msg_text = update.message.text.strip()
            if len(msg_text) == 5 and msg_text.isalnum():
                from pairing import claim_code
                if claim_code(msg_text.upper(), chat_id):
                    await update.message.reply_text(t("chat_paired", get_setting("region", "es")))
                    return

        if chat_id not in allowed_chats:
            await update.message.reply_text(t("unauthorized", get_setting("region", "es")))
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = get_setting('region', 'es')
    msg = (
        "Hola! Soy Findly. Puedo avisarte de nuevos productos en Wallapop y Vinted 🚀.\n\n"
        "Comandos:\n"
        "/add <busqueda> [precio_min] [precio_max] [km] - Añadir búsqueda\n"
        "/add <url_wallapop_o_vinted> - Añadir búsqueda desde URL\n"
        "/list - Ver búsquedas activas\n"
        "/delete <id> - Eliminar búsqueda"
    )
    await update.message.reply_text(msg)

@restricted
async def add_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Join all args to handle spaces in keywords, then split by comma
    full_text = " ".join(context.args).strip()
    await process_add_search(update, full_text)

@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if ("wallapop.com" in text or "vinted" in text) and "search" in text:
        await process_add_search(update, text)

async def process_add_search(update: Update, full_text: str):
    region = get_setting('region', 'es')
    keywords_str = ""
    min_price = None
    max_price = None
    distance_in_km = None
    platform = "both"

    if "http" in full_text and ("wallapop.com" in full_text or "vinted" in full_text):
        # Parse URL
        try:
            import re
            url_match = re.search(r"(https?://[^\s]+)", full_text)
            if url_match:
                full_text = url_match.group(0)

            import urllib.parse
            parsed = urllib.parse.urlparse(full_text)
            params = urllib.parse.parse_qs(parsed.query)

            if "vinted" in parsed.netloc:
                platform = "vinted"
                if "search_text" not in params:
                    await update.message.reply_text(t("vinted_no_keywords", region))
                    return
                keywords_str = params["search_text"][0]
                if "price_from" in params:
                    try: min_price = float(params["price_from"][0])
                    except ValueError: pass
                if "price_to" in params:
                    try: max_price = float(params["price_to"][0])
                    except ValueError: pass
            else:
                platform = "wallapop"
                if "keywords" not in params:
                    await update.message.reply_text(t("url_no_keywords", region))
                    return
                    
                keywords_str = params["keywords"][0]
                
                if "min_sale_price" in params:
                    try: min_price = float(params["min_sale_price"][0])
                    except ValueError: pass
                
                if "max_sale_price" in params:
                    try: max_price = float(params["max_sale_price"][0])
                    except ValueError: pass

                if "distance_in_km" in params:
                    try: distance_in_km = int(params["distance_in_km"][0])
                    except ValueError: pass
                    
        except Exception as e:
            await update.message.reply_text(t("url_error", region, e=e))
            return
            
    else:
        # Parse comma separated
        parts = [p.strip() for p in full_text.split(",")]

        if not parts or not parts[0]:
            await update.message.reply_text(t("usage_add", region))
            return

        keywords_str = parts[0]
        platform = "both"

        if len(parts) > 1:
            try:
                min_price = float(parts[1])
            except ValueError:
                await update.message.reply_text(t("min_price_num", region))
                return

        if len(parts) > 2:
            try:
                max_price = float(parts[2])
            except ValueError:
                await update.message.reply_text(t("max_price_num", region))
                return

    db: Session = get_db_session()
    try:
        search = Search(
            chat_id=update.effective_chat.id,
            keywords=keywords_str,
            min_price=min_price,
            max_price=max_price,
            distance_in_km=distance_in_km,
            platform=platform
        )
        db.add(search)
        db.commit()
        await update.message.reply_text(t("search_saved", region, platform=platform, keywords=keywords_str, min_price=min_price, max_price=max_price))
    except Exception as e:
        await update.message.reply_text(t("save_error", region, e=e))
    finally:
        db.close()

@restricted
async def list_searches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = get_setting('region', 'es')
    db: Session = get_db_session()
    try:
        searches = db.query(Search).filter(Search.chat_id == update.effective_chat.id).all()
        if not searches:
            await update.message.reply_text("📒 No tienes búsquedas activas.")
            return
        
        msg = "📒 Tus búsquedas:\n"
        for s in searches:
            min_p = int(s.min_price) if s.min_price is not None else "None"
            max_p = int(s.max_price) if s.max_price is not None else "None"
            
            keywords_display = f"<b>'{s.keywords}'</b>"
            if s.distance_in_km:
                keywords_display += " 🌎"
            
            plat = getattr(s, 'platform', 'wallapop') or 'both'
            plat_icon = "🟢" if plat == "wallapop" else ("🔵" if plat == "vinted" else "🟢🔵")
                
            msg += f"ID: {s.id} | {plat_icon} {keywords_display} | 💶 {min_p}-{max_p}\n"
        await update.message.reply_text(msg, parse_mode="HTML")
    finally:
        db.close()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = get_setting('region', 'es')
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("delete_"):
        try:
            search_id = int(data.split("_")[1])
            db = SessionLocal()
            try:
                search = db.query(Search).filter(Search.id == search_id, Search.chat_id == query.message.chat_id).first()
                if search:
                    # Optional: delete associated SeenItem
                    db.query(SeenItem).filter(SeenItem.search_id == search.id).delete()
                    db.delete(search)
                    db.commit()
                    
                    # Update message to remove the button and add confirmation
                    if query.message.caption:
                        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ <i>Búsqueda eliminada.</i>", parse_mode="HTML", reply_markup=None)
                    else:
                        await query.edit_message_text(text=query.message.text + t("search_deleted_inline", region), parse_mode="HTML", reply_markup=None)
                else:
                    await query.message.reply_text(t("search_already_deleted", region))
            finally:
                db.close()
        except ValueError:
            pass


@restricted
async def delete_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = get_setting('region', 'es')
    if not context.args:
        await update.message.reply_text(t("usage_delete", region))
        return
    
    try:
        search_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(t("id_must_be_num", region))
        return

    db: Session = get_db_session()
    try:
        search = db.query(Search).filter(Search.id == search_id, Search.chat_id == update.effective_chat.id).first()
        if search:
            db.delete(search)
            db.commit()
            await update.message.reply_text(t("search_deleted", region, id=search_id))
        else:
            await update.message.reply_text(t("search_not_found", region))
    finally:
        db.close()

