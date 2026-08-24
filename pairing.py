import time
import random
import string

active_codes = {}

def generate_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    active_codes[code] = {"expires": time.time() + 50, "chat_id": None}
    return code

def get_code_status(code):
    data = active_codes.get(code)
    if not data:
        return {"status": "not_found"}
    if time.time() > data["expires"]:
        del active_codes[code]
        return {"status": "expired"}
    if data["chat_id"]:
        chat_id = data["chat_id"]
        del active_codes[code]
        return {"status": "success", "chat_id": chat_id}
    return {"status": "pending"}

def claim_code(code, chat_id):
    data = active_codes.get(code)
    if data and time.time() <= data["expires"]:
        data["chat_id"] = chat_id
        return True
    return False
