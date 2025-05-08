import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os

# Configuración inicial
st.set_page_config(page_title="Mi Biblioteca", layout="wide")
st.title("Mi Biblioteca Personal")

# Parámetros de conexión desde variables de entorno
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "biblioteca")
DB_USER = os.environ.get("DB_USER", "pamela")
DB_PASS = os.environ.get("DB_PASS", "clave123")

# Crear conexión con SQLAlchemy
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Crear tabla si no existe
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS libros (
            id SERIAL PRIMARY KEY,
            titulo TEXT,
            autor TEXT,
            puntuacion INTEGER,
            estado TEXT,
            anio INTEGER,
            pendiente_comprar TEXT,
            cita TEXT,
            releido BOOLEAN
        )
    """))
    conn.commit()

# Leer libros existentes
def cargar_libros():
    return pd.read_sql("SELECT * FROM libros ORDER BY id DESC", engine)

# Función para eliminar un libro por ID
def eliminar_libro(id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM libros WHERE id = :id"), {"id": id})
        conn.commit()

# Inicializar estado
if "recargar" not in st.session_state:
    st.session_state["recargar"] = False

# Formulario para agregar nuevos libros
st.sidebar.header("➕ Agregar libro")
with st.sidebar.form("form_agregar", clear_on_submit=True):
    titulo = st.text_input("Título")
    autor = st.text_input("Autor")
    puntuacion = st.radio("Puntuación (1 a 5)", options=[1, 2, 3, 4, 5], horizontal=True)
    estado = st.selectbox("Estado", ["Por leer", "Leyendo", "Terminado"])
    anio = st.number_input("Año", min_value=2024, max_value=2100, step=1, format="%d")
    pendiente = st.selectbox("Pendiente comprar", ["No", "SI", "Ya lo tengo"])
    cita = st.text_area("Cita o comentario")
    releido = st.checkbox("¿Releído?")
    enviado = st.form_submit_button("Guardar libro")

if enviado and titulo:
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO libros (titulo, autor, puntuacion, estado, anio, pendiente_comprar, cita, releido)
            VALUES (:titulo, :autor, :puntuacion, :estado, :anio, :pendiente, :cita, :releido)
        """), {
            "titulo": titulo,
            "autor": autor,
            "puntuacion": puntuacion,
            "estado": estado,
            "anio": anio,
            "pendiente": pendiente,
            "cita": cita,
            "releido": releido
        })
        conn.commit()
    st.toast("✅ Libro agregado correctamente.", icon='📖')
    st.session_state["recargar"] = True

# Mostrar lista de libros con opción de eliminar
st.subheader("📖 Libros registrados")
if st.session_state.get("recargar"):
    libros = cargar_libros()
    st.session_state["recargar"] = False
else:
    libros = cargar_libros()

if not libros.empty:
    for index, row in libros.iterrows():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"**{row['titulo']}** ({row['autor']}) — {row['anio']}")
            st.markdown(f"⭐ {row['puntuacion']} | Estado: {row['estado']} | Releído: {'✅' if row['releido'] else '❌'}")
            st.markdown(f"📝 _{row['cita']}_")
            st.markdown(f"🛒 Pendiente comprar: {row['pendiente_comprar']}")
            st.markdown("---")
        with col2:
            if st.button("🗑️", key=f"delete_{row['id']}"):
                eliminar_libro(row['id'])
                st.toast(f"Libro '{row['titulo']}' eliminado.", icon='❌')
                st.session_state["recargar"] = True
                st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)
                st.stop()
else:
    st.info("No hay libros registrados aún.")

