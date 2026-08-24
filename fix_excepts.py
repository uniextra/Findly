import re

with open("web.py", "r", encoding="utf-8") as f:
    web = f.read()

# Fix bare except
web = web.replace("    except:\n        pass\n    return None, None", "    except (ValueError, KeyError, IndexError):\n        pass\n    return None, None")

# Fix blind exception returning 500 without logging
web = web.replace("    except Exception as e:\n        print(f\"Error in geocoding proxy: {e}\")", "    except (requests.RequestException, ValueError) as e:\n        print(f\"Error in geocoding proxy: {e}\")")

with open("web.py", "w", encoding="utf-8") as f:
    f.write(web)
    
with open("database.py", "r", encoding="utf-8") as f:
    db = f.read()

db = re.sub(r'        except Exception:\n            pass', '        except Exception as e:\n            print(f"Migration error: {e}")', db)
with open("database.py", "w", encoding="utf-8") as f:
    f.write(db)

with open("scheduler.py", "r", encoding="utf-8") as f:
    sched = f.read()
sched = sched.replace("            except:\n                chat_ids = []", "            except ValueError:\n                chat_ids = []")
with open("scheduler.py", "w", encoding="utf-8") as f:
    f.write(sched)

