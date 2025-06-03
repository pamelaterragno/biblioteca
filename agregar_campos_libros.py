import requests

def completar_datos_libro(titulo, autor=""):
    query = f"intitle:{titulo.strip()}"
    if autor.strip():
        query += f"+inauthor:{autor.strip()}"
    query = query.replace(" ", "+")

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" not in data or len(data["items"]) == 0:
            return {
                "titulo": titulo.strip(),
                "autor": autor.strip(),
                "anio_publicacion": None,
                "isbn": None,
                "editorial": None,
                "idioma": None
            }

        info = data["items"][0]["volumeInfo"]

        # Extraer título y autores también
        titulo_api = info.get("title", titulo.strip())
        autores_api = ", ".join(info.get("authors", [autor.strip()])) if info.get("authors") else autor.strip()

        año = info.get("publishedDate", "")[:4] if "publishedDate" in info else None
        isbn = None
        if "industryIdentifiers" in info:
            for id_ in info["industryIdentifiers"]:
                if id_["type"] in ("ISBN_13", "ISBN_10"):
                    isbn = id_["identifier"]
                    break

        editorial = info.get("publisher")
        idioma = info.get("language")

        return {
            "titulo": titulo_api,
            "autor": autores_api,
            "anio_publicacion": int(año) if año and año.isdigit() else None,
            "isbn": isbn,
            "editorial": editorial,
            "idioma": idioma
        }

    except Exception as e:
        print(f"Error al consultar Google Books: {e}")
        return {
            "titulo": titulo.strip(),
            "autor": autor.strip(),
            "anio_publicacion": None,
            "isbn": None,
            "editorial": None,
            "idioma": None
        }
