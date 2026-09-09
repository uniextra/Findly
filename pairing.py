import time
import random
import string
import threading

active_codes = {}
_lock = threading.Lock()

def _prune_expired():
    now = time.time()
    expired = [k for k, v in active_codes.items() if now > v.get("expires", 0)]
    for k in expired:
        active_codes.pop(k, None)

def generate_code():
    with _lock:
        _prune_expired()
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        active_codes[code] = {"expires": time.time() + 50, "chat_id": None}
        return code

def get_code_status(code):
    with _lock:
        data = active_codes.get(code)
        if not data:
            return {"status": "not_found"}
        if time.time() > data["expires"]:
            active_codes.pop(code, None)
            return {"status": "expired"}
        if data["chat_id"]:
            chat_id = data["chat_id"]
            active_codes.pop(code, None)
            return {"status": "success", "chat_id": chat_id}
        return {"status": "pending"}

def claim_code(code, chat_id):
    with _lock:
        data = active_codes.get(code)
        if data and time.time() <= data["expires"]:
            data["chat_id"] = chat_id
            return True
        return False
