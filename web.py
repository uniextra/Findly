import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import SessionLocal, Search, SeenItem, AppSetting, get_setting

app = FastAPI(title="Findly Web UI")

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
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

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
        "allowed_chat_ids": get_setting("allowed_chat_ids", "")
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
                "created_at": s.created_at.isoformat() if s.created_at else None
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
