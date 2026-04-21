"""
db_connection.py — Reads credentials from config.ini and creates the
SQLAlchemy engine + session factory.  Mirrors the sample code pattern.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

userid:   str = config['credentials']['userid']
password: str = config['credentials']['password']
host:     str = config['credentials']['host']
port:     str = config['credentials']['port']
database: str = config['credentials']['database']

db_url:         str = f"postgresql+psycopg2://{userid}:{password}@{host}:{port}/{database}"
db_url_display: str = f"postgresql+psycopg2://{userid}:********@{host}:{port}/{database}"

print("DB URL: " + db_url_display)

engine = create_engine(db_url, pool_size=5, pool_recycle=3600, echo=False)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
