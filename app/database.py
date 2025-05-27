from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
# DATABASE_URL = "postgresql://postgres:Lu1sg4m2z2o2o@db.wfojlrhaxxgxcfoimhgj.supabase.co:5432/MarkNotes"

URL_DATABASE = os.getenv("DATABASE_URL")
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()