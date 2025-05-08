#!/bin/bash

echo "🚀 Iniciando contenedores Streamlit + PostgreSQL (con build)..."

# Forzar reconstrucción de imágenes con los últimos cambios en el código
docker compose up --build -d

# Esperar unos segundos para que arranque
sleep 2

echo "📦 Contenedores activos:"
docker ps --filter name=streamlit_libros

# Guardar logs en segundo plano
docker logs -f streamlit_libros-app-1 > app.log 2>&1 &

echo "📄 Log de la app guardado en app.log (modo background)"
echo "🌐 Accedé a la app en: http://localhost:8501"
