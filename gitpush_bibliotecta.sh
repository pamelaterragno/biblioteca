#!/bin/bash

# Ruta del repositorio local
REPO_DIR="/home/pamela/PROYECTOS/streamlit_libros"

# Mensaje opcional de commit (si no se pasa, usa un mensaje por defecto)
MENSAJE=${1:-"📝 Commit automático desde streamlit_libros"}

# Ir a la carpeta del proyecto
cd "$REPO_DIR" || { echo "❌ No se pudo acceder al directorio $REPO_DIR"; exit 1; }

# Agregar todos los cambios
git add .

# Hacer commit
git commit -m "$MENSAJE"

# Hacer push
git push origin main
