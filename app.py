import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
import subprocess
from agregar_campos_libros import completar_datos_libro

# 🧩 Configuración inicial
st.set_page_config(page_title="Mi Biblioteca", layout="wide")
st.title("📚 Mi Biblioteca Personal")

# 🌐 Parámetros de conexión desde variables de entorno
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "biblioteca")
DB_USER = os.environ.get("DB_USER", "pamela")
DB_PASS = os.environ.get("DB_PASS", "clave123")

# 🔌 Crear conexión con SQLAlchemy
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# 🛠️ Crear tabla si no existe (¡agregá las columnas nuevas si no están!)
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS libros (
            id SERIAL PRIMARY KEY,
            titulo TEXT,
            autor TEXT,
            puntuacion INTEGER,
            estado TEXT,
            anio_lectura INTEGER,
            pendiente_comprar TEXT,
            cita TEXT,
            releido BOOLEAN,
            anio_publicacion INTEGER,
            isbn VARCHAR(20),
            editorial TEXT,
            idioma VARCHAR(10)
        )
    """))
    conn.commit()

# 🔄 Botón para completar datos faltantes desde Google Books API
if st.button("🔄 Completar datos faltantes:"):
    with st.spinner("Completando datos..."):
        try:
            result = subprocess.run(["python", "completar_datos_bdd.py"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Datos completados correctamente.")
                st.text(result.stdout)
                st.session_state["recargar"] = True
            else:
                st.error("❌ Hubo un error al ejecutar el script.")
                st.text(result.stderr)
        except Exception as e:
            st.error(f"❌ Error al ejecutar el script: {e}")

# 📥 Leer libros desde base
def cargar_libros():
    return pd.read_sql("SELECT * FROM libros ORDER BY id DESC", engine)

# 🗑️ Eliminar libro
def eliminar_libro(id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM libros WHERE id = :id"), {"id": id})
        conn.commit()

# 🔁 Estado inicial
if "recargar" not in st.session_state:
    st.session_state["recargar"] = False

# ➕ Formulario para agregar libros
st.sidebar.header("➕ Agregar libro")
with st.sidebar.form("form_agregar", clear_on_submit=True):
    titulo = st.text_input("Título")
    autor = st.text_input("Autor")
    puntuacion = st.radio("Puntuación (1 a 5)", options=[1, 2, 3, 4, 5], horizontal=True)
    estado = st.selectbox("Estado", ["Por leer", "Leyendo", "Terminado"])
    anio_lectura = st.number_input("Año", min_value=2024, max_value=2100, step=1, format="%d")
    pendiente = st.selectbox("Pendiente comprar", ["No", "SI", "Ya lo tengo"])
    cita = st.text_area("Cita o comentario")
    releido = st.checkbox("¿Releído?")
    enviado = st.form_submit_button("Guardar libro")

if enviado and titulo:
    datos_extra = completar_datos_libro(titulo, autor)
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO libros (
                titulo, autor, puntuacion, estado, anio_lectura,
                pendiente_comprar, cita, releido,
                anio_publicacion, isbn, editorial, idioma
            )
            VALUES (
                :titulo, :autor, :puntuacion, :estado, :anio_lectura,
                :pendiente, :cita, :releido,
                :anio_publicacion, :isbn, :editorial, :idioma
            )
        """), {
            "titulo": titulo,
            "autor": autor,
            "puntuacion": puntuacion,
            "estado": estado,
            "anio_lectura": anio_lectura,
            "pendiente": pendiente,
            "cita": cita,
            "releido": releido,
            "anio_publicacion": datos_extra.get("anio_publicacion"),
            "isbn": datos_extra.get("isbn"),
            "editorial": datos_extra.get("editorial"),
            "idioma": datos_extra.get("idioma")
        })
        conn.commit()
    st.toast("✅ Libro agregado correctamente.", icon='📖')
    st.session_state["recargar"] = True



# 📋 Mostrar libros registrados
st.subheader("📖 Libros registrados")

# 🔍 Filtro por búsqueda
busqueda = st.text_input("🔎 Buscar por título o autor")

libros = cargar_libros() if st.session_state["recargar"] else cargar_libros()
st.session_state["recargar"] = False

if busqueda:
    libros = libros[
        libros['titulo'].str.contains(busqueda, case=False, na=False) |
        libros['autor'].str.contains(busqueda, case=False, na=False)
    ]
if not libros.empty:
    for index, row in libros.iterrows():
        col1, col2 = st.columns([6, 1])
        with col1:
            # expander
            titulo_visible = f"{row['titulo']} — {row['autor']} — {row['anio_lectura']}"
            with st.expander(titulo_visible, expanded=False):
                st.markdown(
                    f"""
                    <ul style='font-size:14px; line-height: 1.6'>
                        <li>⭐ <b>Puntuación:</b> {row['puntuacion']}</li>
                        <li>📘 <b>Estado:</b> {row['estado']}</li>
                        <li>🔁 <b>Releído:</b> {'✅' if row['releido'] else '❌'}</li>
                        <li>📝 <i>{row['cita']}</i></li>
                        <li>🛒 <b>Pendiente comprar:</b> {row['pendiente_comprar']}</li>
                        <li>🗓️  <b>Publicado en:</b> {row['anio_publicacion'] or 'Desconocido'}</li>
                        <li>🔤 <b>Idioma:</b> {row['idioma'] or 'Desconocido'}</li>
                        <li>🏢 <b>Editorial:</b> {row['editorial'] or 'Desconocido'}</li>
                        <li>🔢 <b>ISBN:</b> {row['isbn'] or 'Desconocido'}</li>
                    </ul>
                    """,
                    unsafe_allow_html=True
                )
        with col2:
            if st.button("🗑️ ", key=f"delete_{row['id']}"):
                eliminar_libro(row['id'])
                st.toast(f"Libro '{row['titulo']}' eliminado.", icon='❌')
                st.session_state["recargar"] = True
                st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)
                st.stop()



else:
    st.info("No hay libros registrados aún.")

