import requests

def completar_datos_libro(titulo, autor=""):
    query = f"{titulo} {autor}".strip().replace(" ", "+")
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&maxResults=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" not in data or len(data["items"]) == 0:
            return {"año": None, "isbn": None, "editorial": None, "idioma": None}

        info = data["items"][0]["volumeInfo"]

        # Extraer datos
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
            "año": int(año) if año and año.isdigit() else None,
            "isbn": isbn,
            "editorial": editorial,
            "idioma": idioma
        }

    except Exception as e:
        print(f"Error al consultar Google Books: {e}")
        return {"año": None, "isbn": None, "editorial": None, "idioma": None}
