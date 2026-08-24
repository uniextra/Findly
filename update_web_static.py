import re

with open("web.py", "r", encoding="utf-8") as f:
    web = f.read()

web_replace = """from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import SessionLocal, Search, SeenItem, AppSetting, get_setting

app = FastAPI(title="Findly Web UI")
app.mount("/static", StaticFiles(directory="static"), name="static")"""

web = re.sub(r'from fastapi import FastAPI.*?app = FastAPI\(title="Findly Web UI"\)', web_replace, web, flags=re.DOTALL)

with open("web.py", "w", encoding="utf-8") as f:
    f.write(web)
