import streamlit as st
import pandas as pd
import plotly.express as px
from db import engine, conectar_db
from sqlalchemy import text

def obtener_id_usuario(username):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return user_id

def mostrar_estadisticas():
    st.title("📊 Estadísticas de Libros")

    usuario = st.session_state.get("usuario")
    if not usuario:
        st.warning("No hay usuario logueado.")
        return

    usuario_id = obtener_id_usuario(usuario)

    try:
        query = text("SELECT * FROM libros WHERE usuario_id = :usuario_id")
        df = pd.read_sql_query(query, engine, params={"usuario_id": usuario_id})
    except Exception as e:
        st.error(f"Error al conectar o leer datos: {e}")
        return

    if df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric("📚 Total de libros", len(df))

        if "puntuacion" in df.columns:
            prom = df["puntuacion"].dropna().mean()
            st.metric("⭐ Promedio de puntuación", f"{prom:.2f}")

    # Libros por año de lectura
    if "anio_lectura" in df.columns:
        st.subheader("📅 Libros por Año de Lectura")
        conteo_anio = df["anio_lectura"].value_counts().sort_index()
        fig = px.bar(x=conteo_anio.index, y=conteo_anio.values,
                     labels={"x": "Año", "y": "Cantidad"},
                     title="Cantidad de libros por año")
        st.plotly_chart(fig, use_container_width=True)

    # Estado de lectura
    if "estado" in df.columns:
        st.subheader("📘 Estado de Lectura")
        conteo_estado = df["estado"].value_counts()
        fig = px.pie(names=conteo_estado.index, values=conteo_estado.values,
                     title="Distribución por estado")
        st.plotly_chart(fig, use_container_width=True)

    # Autores más leídos
    if "autor" in df.columns:
        st.subheader("👩‍💼 Autores más Leídos")
        conteo_autores = df["autor"].value_counts().head(10)
        fig = px.bar(x=conteo_autores.values, y=conteo_autores.index,
                     orientation='h', labels={"x": "Cantidad", "y": "Autor"},
                     title="Top 10 autores más leídos")
        st.plotly_chart(fig, use_container_width=True)

    # Puntuaciones
    if "puntuacion" in df.columns:
        st.subheader("⭐ Distribución de Puntuaciones")
        puntuacion_count = df["puntuacion"].value_counts().sort_index()
        fig = px.bar(x=puntuacion_count.index, y=puntuacion_count.values,
                     labels={"x": "Puntuación", "y": "Cantidad"},
                     title="Cantidad de libros por puntuación")
        st.plotly_chart(fig, use_container_width=True)
