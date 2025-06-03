import streamlit as st 
import pandas as pd
from sqlalchemy import text
from agregar_campos_libros import completar_datos_libro
from mostrar_estadisticas import mostrar_estadisticas
from buscador import buscar_libros
from auth import login_y_registro, app_principal
from db import engine, conectar_db  # Agrego conectar_db para obtener usuario_id

# Configuración inicial
st.set_page_config(page_title="Mi Biblioteca", layout="wide")
st.title("Mi Biblioteca Personal")

# Login obligatorio antes de cargar el resto de la app
if "usuario" not in st.session_state:
    login_y_registro()
    st.stop() 
else:
    app_principal()

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
            idioma VARCHAR(10),
            usuario_id INTEGER REFERENCES usuarios(id)
        )
    """))
    conn.commit()

def obtener_id_usuario(username):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return user_id

# Tabs de navegación
tab1, tab2 = st.tabs(["Libros", "Estadísticas"])

with tab1:
    def cargar_libros():
        usuario = st.session_state.get("usuario")
        if not usuario:
            return pd.DataFrame()

        usuario_id = obtener_id_usuario(usuario)

        query = text("SELECT * FROM libros WHERE usuario_id = :usuario_id ORDER BY id DESC")
        df = pd.read_sql_query(query, engine, params={"usuario_id": usuario_id})

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

    # Formulario para agregar libro
    st.sidebar.header("Agregar libro")
    with st.sidebar.form("form_agregar", clear_on_submit=True):
        titulo_input = st.text_input("Título")
        autor_input = st.text_input("Autor")
        puntuacion = st.radio("Puntuación (1 a 5)", options=[1, 2, 3, 4, 5], horizontal=True)
        estado = st.selectbox("Estado", ["Por leer", "Leyendo", "Terminado"])
        anio_lectura = st.number_input("Año", min_value=2024, max_value=2100, step=1, format="%d")
        pendiente = st.selectbox("Pendiente comprar", ["No", "SI", "Ya lo tengo"])
        cita = st.text_area("Cita o comentario")
        releido = st.checkbox("¿Releído?")
        enviado = st.form_submit_button("Guardar libro")

    if enviado and titulo_input:
        datos_extra = completar_datos_libro(titulo_input.strip(), autor_input.strip() if autor_input else None)

        usuario_id = obtener_id_usuario(st.session_state["usuario"])

        # Usamos los datos completados si están
        titulo_final = datos_extra.get("titulo", titulo_input.strip())
        autor_final = datos_extra.get("autor", autor_input.strip())

        # Verificar si ya existe el libro para este usuario
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id FROM libros
                WHERE LOWER(titulo) = LOWER(:titulo) AND LOWER(autor) = LOWER(:autor) AND usuario_id = :usuario_id
            """), {
                "titulo": titulo_final,
                "autor": autor_final,
                "usuario_id": usuario_id
            }).fetchone()

            if result:
                st.warning(f"El libro '{titulo_final}' por '{autor_final}' ya existe en tu biblioteca.")
            else:
                conn.execute(text("""
                    INSERT INTO libros (
                        titulo, autor, puntuacion, estado, anio_lectura,
                        pendiente_comprar, cita, releido,
                        anio_publicacion, isbn, editorial, idioma, usuario_id
                    )
                    VALUES (
                        :titulo, :autor, :puntuacion, :estado, :anio_lectura,
                        :pendiente, :cita, :releido,
                        :anio_publicacion, :isbn, :editorial, :idioma, :usuario_id
                    )
                """), {
                    "titulo": titulo_final,
                    "autor": autor_final,
                    "puntuacion": puntuacion,
                    "estado": estado,
                    "anio_lectura": anio_lectura,
                    "pendiente": pendiente,
                    "cita": cita,
                    "releido": releido,
                    "anio_publicacion": datos_extra.get("anio_publicacion"),
                    "isbn": datos_extra.get("isbn"),                         
                    "editorial": datos_extra.get("editorial"),               
                    "idioma": datos_extra.get("idioma"),
                    "usuario_id": usuario_id
                })
                conn.commit()
                st.toast("Libro agregado correctamente.")
                st.session_state["recargar"] = True

    # Buscador
    st.subheader("Libros registrados")

    with st.expander("Búsqueda avanzada"):
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
                            <li>Puntuación: {row['puntuacion'] if not pd.isna(row['puntuacion']) else 'Desconocido'}</li>
                            <li>Estado: {row['estado'] if not pd.isna(row['estado']) else 'Desconocido'}</li>
                            <li>Releído: {'Sí' if row['releido'] == True else 'No' if row['releido'] == False else 'Desconocido'}</li>
                            <li>Cita: {row['cita'] if not pd.isna(row['cita']) else 'Sin cita'}</li>
                            <li>Pendiente comprar: {row['pendiente_comprar'] if not pd.isna(row['pendiente_comprar']) else 'Desconocido'}</li>
                            <li>Publicado en: {row['anio_publicacion'] if not pd.isna(row['anio_publicacion']) else 'Desconocido'}</li>
                            <li>Idioma: {row['idioma'] if not pd.isna(row['idioma']) else 'Desconocido'}</li>
                            <li>Editorial: {row['editorial'] if not pd.isna(row['editorial']) else 'Desconocido'}</li>
                            <li>ISBN: {row['isbn'] if not pd.isna(row['isbn']) else 'Desconocido'}</li>
                        </ul>
                        """,
                        unsafe_allow_html=True
                    )
            with col2:
                if st.button("Eliminar", key=f"delete_{row['id']}"):
                    eliminar_libro(row['id'])
                    st.toast(f"Libro '{row['titulo']}' eliminado.")
                    st.session_state["recargar"] = True
                    st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)
                    st.stop()
    else:
        st.info("No hay libros registrados con los filtros actuales.")

with tab2:
    mostrar_estadisticas()
