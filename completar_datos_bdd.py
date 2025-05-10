import psycopg2
import requests



def completar_datos_libro(titulo, autor=""):
    query = f"intitle:{titulo}"
    if autor:
        query += f"+inauthor:{autor}"

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" not in data or not data["items"]:
            return {
                "anio_publicacion": None,
                "isbn": None,
                "editorial": None,
                "idioma": None
            }

        volume_info = data["items"][0]["volumeInfo"]

        anio = volume_info.get("publishedDate", "")[:4]
        if not anio.isdigit():
            anio = None

        isbn = next(
            (id["identifier"] for id in volume_info.get("industryIdentifiers", [])
             if id["type"] in ["ISBN_13", "ISBN_10"]),
            None
        )

        editorial = volume_info.get("publisher")
        idioma = volume_info.get("language")

        return {
            "anio_publicacion": int(anio) if anio and anio.isdigit() else None,
            "isbn": isbn,
            "editorial": editorial,
            "idioma": idioma
        }

    except Exception as e:
        print(f"❌ Error al obtener datos de Google Books para '{titulo}': {e}")
        return {
            "anio_publicacion": None,
            "isbn": None,
            "editorial": None,
            "idioma": None
        }


# Conexión a PostgreSQL (ajustá credenciales si es necesario)
conn = psycopg2.connect(
    host="db",
    dbname="biblioteca",
    user="pamela",
    password="clave123",
    port=5432  # ajustalo si usás otro puerto
)
cursor = conn.cursor()

# Buscar libros que tengan campos nuevos incompletos
cursor.execute("""
    SELECT id, titulo, autor
    FROM libros
    WHERE anio_publicacion IS NULL
       OR isbn IS NULL
       OR editorial IS NULL
       OR idioma IS NULL
""")

libros = cursor.fetchall()

for id_libro, titulo, autor in libros:
    datos = completar_datos_libro(titulo, autor)

    update_query = """
        UPDATE libros
        SET anio_publicacion = %s,
            isbn = %s,
            editorial = %s,
            idioma = %s
        WHERE id = %s
    """

    cursor.execute(update_query, (
        datos["anio_publicacion"],
        datos["isbn"],
        datos["editorial"],
        datos["idioma"],
        id_libro
    ))

    print(f"✅ Datos actualizados para: {titulo}")

conn.commit()
cursor.close()
conn.close()
print("🟢 ¡Todos los libros fueron completados correctamente!")

