import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from database import SessionLocal, Search, SeenItem

app = FastAPI(title="Findly Web UI")

class SearchCreate(BaseModel):
    keywords: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    distance_in_km: Optional[int] = None
    platform: str = "both"
    # Note: we need a chat_id. Since this is local, we'll fetch the first allowed chat ID from env, or default to 0
    chat_id: Optional[int] = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

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
        # Determine chat_id
        chat_id = search.chat_id
        if not chat_id:
            allowed = os.environ.get("ALLOWED_CHAT_IDS", "")
            if allowed:
                chat_id = int(allowed.split(',')[0].strip("'\" "))
            else:
                chat_id = 123456789 # Fallback
                
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
