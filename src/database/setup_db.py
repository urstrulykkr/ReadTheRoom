from models import Base
from config import DATABASE_URL
from sqlalchemy import create_engine

def setup_database():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)  # Drop all existing tables
    Base.metadata.create_all(engine)  # Create new tables
    print("Database tables created successfully!")

if __name__ == "__main__":
    setup_database() 