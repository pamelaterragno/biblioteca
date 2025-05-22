import psycopg2
import pandas as pd
from typing import Optional

def buscar_libros(
    titulo: Optional[str] = None,
    autor: Optional[str] = None,
    anio_publicacion: Optional[int] = None,
    anio_lectura: Optional[int] = None,
    estado: Optional[str] = None,
    editorial: Optional[str] = None,
    idioma: Optional[str] = None,
    releido: Optional[bool] = None,
    pendiente_comprar: Optional[str] = None,
    puntuacion: Optional[int] = None
) -> pd.DataFrame:

    conn = psycopg2.connect(
        dbname="biblioteca",
        user="pamela",
        password="clave123",
        host="db",
        port="5432"
    )
    cursor = conn.cursor()

    query = "SELECT * FROM libros WHERE 1=1"
    valores = []

    if titulo:
        query += " AND LOWER(titulo) LIKE %s"
        valores.append(f"%{titulo.lower()}%")
    if autor:
        query += " AND LOWER(autor) LIKE %s"
        valores.append(f"%{autor.lower()}%")
    if anio_publicacion:
        query += " AND anio_publicacion = %s"
        valores.append(anio_publicacion)
    if anio_lectura:
        query += " AND anio_lectura = %s"
        valores.append(anio_lectura)
    if estado:
        query += " AND LOWER(estado) = %s"
        valores.append(estado.lower())
    if editorial:
        query += " AND LOWER(editorial) LIKE %s"
        valores.append(f"%{editorial.lower()}%")
    if idioma:
        query += " AND LOWER(idioma) = %s"
        valores.append(idioma.lower())
    if releido is not None:
        query += " AND releido = %s"
        valores.append(releido)
    if pendiente_comprar:
        query += " AND LOWER(pendiente_comprar) = %s"
        valores.append(pendiente_comprar.lower())
    if puntuacion:
        query += " AND puntuacion = %s"
        valores.append(puntuacion)

    cursor.execute(query, valores)
    columnas = [desc[0] for desc in cursor.description]
    resultados = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(resultados, columns=columnas)
    return df
