import os
from sqlalchemy import create_engine
import psycopg2

# Variables de entorno
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "biblioteca")
DB_USER = os.environ.get("DB_USER", "pamela")
DB_PASS = os.environ.get("DB_PASS", "clave123")

# SQLAlchemy Engine para operaciones con Pandas
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Conexión psycopg2 para consultas SQL tradicionales
def conectar_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
