import streamlit as st 
import pandas as pd
from sqlalchemy import create_engine, text
import os
from agregar_campos_libros import completar_datos_libro
from mostrar_estadisticas import mostrar_estadisticas
from buscador import buscar_libros

# Configuración inicial
st.set_page_config(page_title="Mi Biblioteca", layout="wide")
st.title("📚 Mi Biblioteca Personal")

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

# Tabs para navegación
tab1, tab2 = st.tabs(["📚 Libros", "📊 Estadísticas"])

with tab1:
    def cargar_libros():
        df = pd.read_sql("SELECT * FROM libros ORDER BY id DESC", engine)
        for col in ["anio_lectura", "anio_publicacion"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype("Int64")
        return df

    def eliminar_libro(id):
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM libros WHERE id = :id"), {"id": id})
            conn.commit()

    if "recargar" not in st.session_state:
        st.session_state["recargar"] = False

    # --- Formulario para agregar libro ---
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

    # --- Buscador ---
    st.subheader("📖 Libros registrados")

    with st.expander("🔎 Búsqueda avanzada"):
        col1, col2, col3 = st.columns(3)

        with col1:
            titulo_filtro = st.text_input("Título contiene")
            autor_filtro = st.text_input("Autor contiene")
            estado_filtro = st.selectbox("Estado", ["", "Por leer", "Leyendo", "Terminado"])
            idioma_filtro = st.text_input("Idioma exacto")

        with col2:
            anio_publicacion = st.number_input("Año publicación", min_value=0, step=1, format="%d", value=0)
            anio_lectura = st.number_input("Año lectura", min_value=0, step=1, format="%d", value=0)
            editorial_filtro = st.text_input("Editorial contiene")
            pendiente_comprar = st.selectbox("Pendiente comprar", ["", "SI", "No", "Ya lo tengo"])

        with col3:
            puntuacion_filtro = st.selectbox("Puntuación exacta", [""] + [1, 2, 3, 4, 5])
            releido_filtro = st.selectbox("¿Releído?", ["", "Sí", "No"])

        aplicar_filtros = st.button("Aplicar filtros")

    if aplicar_filtros:
        libros = buscar_libros(
            titulo=titulo_filtro or None,
            autor=autor_filtro or None,
            anio_publicacion=anio_publicacion if anio_publicacion else None,
            anio_lectura=anio_lectura if anio_lectura else None,
            estado=estado_filtro or None,
            editorial=editorial_filtro or None,
            idioma=idioma_filtro or None,
            releido=True if releido_filtro == "Sí" else False if releido_filtro == "No" else None,
            pendiente_comprar=pendiente_comprar or None,
            puntuacion=int(puntuacion_filtro) if puntuacion_filtro else None
        )
    else:
        libros = cargar_libros()

    if not libros.empty:
        for index, row in libros.iterrows():
            col1, col2 = st.columns([6, 1])
            with col1:
                titulo_visible = f"{row['titulo']} — {row['autor']} — {row['anio_lectura']}"
                with st.expander(titulo_visible, expanded=False):
                    st.markdown(
                        f"""
                        <ul style='font-size:14px; line-height: 1.6'>
                            <li>⭐ <b>Puntuación:</b> {row['puntuacion'] if not pd.isna(row['puntuacion']) else 'Desconocido'}</li>
                            <li>📘 <b>Estado:</b> {row['estado'] if not pd.isna(row['estado']) else 'Desconocido'}</li>
                            <li>🔁 <b>Releído:</b> {'✅' if row['releido'] == True else '❌' if row['releido'] == False else 'Desconocido'}</li>
                            <li>📝 <i>{row['cita'] if not pd.isna(row['cita']) else 'Sin cita'}</i></li>
                            <li>🛒 <b>Pendiente comprar:</b> {row['pendiente_comprar'] if not pd.isna(row['pendiente_comprar']) else 'Desconocido'}</li>
                            <li>🗓️  <b>Publicado en:</b> {row['anio_publicacion'] if not pd.isna(row['anio_publicacion']) else 'Desconocido'}</li>
                            <li>🔤 <b>Idioma:</b> {row['idioma'] if not pd.isna(row['idioma']) else 'Desconocido'}</li>
                            <li>🏢 <b>Editorial:</b> {row['editorial'] if not pd.isna(row['editorial']) else 'Desconocido'}</li>
                            <li>🔢 <b>ISBN:</b> {row['isbn'] if not pd.isna(row['isbn']) else 'Desconocido'}</li>
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
        st.info("No hay libros registrados con los filtros actuales.")

with tab2:
    mostrar_estadisticas()
