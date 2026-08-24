import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime



# Ensure data directory exists
os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///data/wallatrack.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Search(Base):
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    keywords = Column(String, nullable=False)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    distance_in_km = Column(Integer, nullable=True)
    platform = Column(String, default="both")
    created_at = Column(DateTime, default=datetime.utcnow)

    seen_items = relationship("SeenItem", back_populates="search", cascade="all, delete-orphan")

class SeenItem(Base):
    __tablename__ = "seen_items"

    id = Column(Integer, primary_key=True, index=True)
    wallapop_id = Column(String, unique=True, index=True)
    search_id = Column(Integer, ForeignKey("searches.id"))
    found_at = Column(DateTime, default=datetime.utcnow)

    search = relationship("Search", back_populates="seen_items")



def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Simple migration to add distance_in_km if it doesn't exist
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE searches ADD COLUMN distance_in_km INTEGER"))
            print("Added distance_in_km column to searches table")
        except Exception:
            pass

        # Migration to add platform column
        try:
            conn.execute(text("ALTER TABLE searches ADD COLUMN platform VARCHAR DEFAULT 'both'"))
            print("Added platform column to searches table")
        except Exception:
            # Column likely already exists
            pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
