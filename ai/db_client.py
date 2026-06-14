import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "roadgis"),
        user=os.getenv("DB_USER", "roadgis"),
        password=os.getenv("DB_PASSWORD", "roadgis1234"),
    )
