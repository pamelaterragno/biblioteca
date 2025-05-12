import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

def mostrar_estadisticas():
    st.title("📊 Estadísticas de Libros")

    # Conexión a la base de datos
    engine = create_engine("postgresql://pamela:clave123@db:5432/biblioteca")

    try:
        df = pd.read_sql("SELECT * FROM libros", engine)
    except Exception as e:
        st.error(f"Error al conectar o leer datos: {e}")
        return

    if df.empty:
        st.warning("No hay datos disponibles en la base.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric("📚 Total de libros", len(df))

        if "puntuacion" in df.columns:
            prom = df["puntuacion"].dropna().mean()
            st.metric("⭐ Promedio de puntuación", f"{prom:.2f}")

    # --- Libros por año de lectura ---
    if "anio_lectura" in df.columns:
        st.subheader("📅 Libros por Año de Lectura")
        conteo_anio = df["anio_lectura"].value_counts().sort_index()
        fig = px.bar(x=conteo_anio.index, y=conteo_anio.values,
                     labels={"x": "Año", "y": "Cantidad"},
                     title="Cantidad de libros por año")
        st.plotly_chart(fig, use_container_width=True)

    # --- Estado de lectura ---
    if "estado" in df.columns:
        st.subheader("📘 Estado de Lectura")
        conteo_estado = df["estado"].value_counts()
        fig = px.pie(names=conteo_estado.index, values=conteo_estado.values,
                     title="Distribución por estado")
        st.plotly_chart(fig, use_container_width=True)

    # --- Autores más leídos ---
    if "autor" in df.columns:
        st.subheader("👩‍💼 Autores más Leídos")
        conteo_autores = df["autor"].value_counts().head(10)
        fig = px.bar(x=conteo_autores.values, y=conteo_autores.index,
                     orientation='h', labels={"x": "Cantidad", "y": "Autor"},
                     title="Top 10 autores más leídos")
        st.plotly_chart(fig, use_container_width=True)

    # --- Puntuaciones ---
    if "puntuacion" in df.columns:
        st.subheader("⭐ Distribución de Puntuaciones")
        puntuacion_count = df["puntuacion"].value_counts().sort_index()
        fig = px.bar(x=puntuacion_count.index, y=puntuacion_count.values,
                     labels={"x": "Puntuación", "y": "Cantidad"},
                     title="Cantidad de libros por puntuación")
        st.plotly_chart(fig, use_container_width=True)
