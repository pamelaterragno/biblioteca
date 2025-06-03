import pandas as pd
from typing import Optional
from db import conectar_db

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

    from streamlit import session_state

    usuario = session_state.get("usuario")
    if not usuario:
        return pd.DataFrame()

    # Obtener usuario_id
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (usuario,))
    result = cur.fetchone()
    if not result:
        cur.close()
        conn.close()
        return pd.DataFrame()

    usuario_id = result[0]

    query = "SELECT * FROM libros WHERE usuario_id = %s"
    valores = [usuario_id]

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

    cur.execute(query, valores)
    columnas = [desc[0] for desc in cur.description]
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(resultados, columns=columnas)
    return df
