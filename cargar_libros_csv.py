import pandas as pd
import sys
from db import engine 

# Verificación de argumento
if len(sys.argv) != 2:
    print("Uso: python cargar_libros_csv.py ruta/al/archivo.csv")
    sys.exit(1)

csv_path = sys.argv[1]

df = pd.read_csv(csv_path)

# Renombrar columnas para que coincidan con la base
df = df.rename(columns={
    "Título": "titulo",
    "Autor": "autor",
    "Puntuación (0-5)": "puntuacion",
    "Estado": "estado",
    "Año": "anio_lectura",
    "Pendiente comprar": "pendiente_comprar",
    "Cita": "cita",
    "Reeleído": "releido"
})

# Convertir puntuación a número
def convertir_puntuacion(val):
    if isinstance(val, str) and val.startswith("⭐"):
        return val.count("⭐")
    try:
        return int(val)
    except:
        return None

df["puntuacion"] = df["puntuacion"].apply(convertir_puntuacion)

# Convertir releído a booleano
df["releido"] = df["releido"].fillna(False).apply(lambda x: str(x).strip().lower() in ["si", "true", "1"])

# Completar columnas faltantes
df["anio_publicacion"] = None
df["isbn"] = None
df["editorial"] = None
df["idioma"] = None

# Inserción en la base
df.to_sql("libros", engine, if_exists="append", index=False)

print(f"Datos insertados correctamente desde {csv_path}")