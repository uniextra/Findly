import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import SessionLocal, Search, SeenItem, AppSetting, get_setting
from pairing import generate_code, get_code_status

app = FastAPI(title="Findly Web UI")
app.mount("/static", StaticFiles(directory="static"), name="static")

class SearchCreate(BaseModel):
    keywords: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    distance_in_km: Optional[int] = None
    platform: str = "both"
    chat_id: Optional[int] = None

class SettingUpdate(BaseModel):
    key: str
    value: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/pairing/generate")
def api_generate_code():
    code = generate_code()
    return {"code": code}

@app.get("/api/pairing/status")
def api_pairing_status(code: str):
    return get_code_status(code)

@app.get("/api/stats")
def get_stats():
    db = SessionLocal()
    try:
        active_searches = db.query(Search).count()
        total_items = db.query(SeenItem).count()
        # Status could be determined by checking if token is set
        token = get_setting("telegram_token")
        bot_status = "Active" if token else "Waiting for Token"
        return {
            "active_searches": active_searches,
            "total_items": total_items,
            "bot_status": bot_status
        }
    finally:
        db.close()

@app.get("/api/settings")
def get_settings():
    return {
        "telegram_token": get_setting("telegram_token", ""),
        "allowed_chat_ids": get_setting("allowed_chat_ids", ""),
        "region": get_setting("region", "es"),
        "wallapop_interval": get_setting("wallapop_interval", "5"),
        "vinted_interval": get_setting("vinted_interval", "5")
    }

@app.post("/api/settings")
def save_settings(settings: List[SettingUpdate]):
    db = SessionLocal()
    try:
        for s in settings:
            existing = db.query(AppSetting).filter(AppSetting.key == s.key).first()
            if existing:
                existing.value = s.value
            else:
                db.add(AppSetting(key=s.key, value=s.value))
        db.commit()
        # Trigger bot restart
        from main import restart_bot
        restart_bot()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/items")
def get_items():
    db = SessionLocal()
    try:
        items = db.query(SeenItem).order_by(SeenItem.found_at.desc()).limit(200).all()
        return [
            {
                "id": i.id,
                "platform_id": i.wallapop_id,
                "search_id": i.search_id,
                "search_keywords": i.search.keywords if i.search else "Deleted Search",
                "found_at": i.found_at.isoformat() if i.found_at else None,
                "title": i.title,
                "price": i.price,
                "url": i.url
            }
            for i in items
        ]
    finally:
        db.close()

@app.get("/api/searches")
def get_searches():
    db = SessionLocal()
    try:
        searches = db.query(Search).all()
        return [
            {
                "id": s.id,
                "keywords": s.keywords,
                "min_price": s.min_price,
                "max_price": s.max_price,
                "distance_in_km": s.distance_in_km,
                "platform": s.platform,
                "chat_id": s.chat_id,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "last_checked_at": s.last_checked_at.isoformat() if s.last_checked_at else None
            }
            for s in searches
        ]
    finally:
        db.close()

@app.post("/api/searches")
def add_search(search: SearchCreate):
    db = SessionLocal()
    try:
        chat_id = search.chat_id
        if not chat_id:
            allowed = get_setting("allowed_chat_ids", "")
            if allowed:
                chat_id = int(allowed.split(',')[0].strip("'\" "))
            else:
                chat_id = 123456789
                
        new_search = Search(
            chat_id=chat_id,
            keywords=search.keywords,
            min_price=search.min_price,
            max_price=search.max_price,
            distance_in_km=search.distance_in_km,
            platform=search.platform
        )
        db.add(new_search)
        db.commit()
        db.refresh(new_search)
        return {"success": True, "id": new_search.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.put("/api/searches/{search_id}")
def update_search(search_id: int, search: SearchCreate):
    db = SessionLocal()
    try:
        existing = db.query(Search).filter(Search.id == search_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Search not found")
        
        existing.keywords = search.keywords
        existing.min_price = search.min_price
        existing.max_price = search.max_price
        existing.distance_in_km = search.distance_in_km
        existing.platform = search.platform
        if search.chat_id:
            existing.chat_id = search.chat_id
            
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/searches/{search_id}/refresh")
def refresh_search(search_id: int):
    import asyncio
    from main import global_loop, global_queue
    from scheduler import check_single_search
    
    if global_loop is None or global_queue is None:
        raise HTTPException(status_code=500, detail="Bot is not running, cannot refresh.")
        
    db = SessionLocal()
    try:
        search = db.query(Search).filter(Search.id == search_id).first()
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
            
        asyncio.run_coroutine_threadsafe(check_single_search(search_id, global_queue), global_loop)
        return {"success": True}
    finally:
        db.close()

@app.delete("/api/searches/{search_id}")
def delete_search(search_id: int):
    db = SessionLocal()
    try:
        search = db.query(Search).filter(Search.id == search_id).first()
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
        
        db.query(SeenItem).filter(SeenItem.search_id == search.id).delete()
        db.delete(search)
        db.commit()
        return {"success": True}
    finally:
        db.close()
