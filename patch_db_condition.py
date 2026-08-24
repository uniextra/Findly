import re

with open("database.py", "r", encoding="utf-8") as f:
    db_code = f.read()

# Add condition column
db_code = db_code.replace('distance_in_km = Column(Integer, nullable=True)', 'distance_in_km = Column(Integer, nullable=True)\n    condition = Column(String, nullable=True)')

with open("database.py", "w", encoding="utf-8") as f:
    f.write(db_code)
