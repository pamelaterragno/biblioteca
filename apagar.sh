#!/bin/bash

echo "🛑 Deteniendo contenedores Streamlit + PostgreSQL..."

# Detener y eliminar contenedores
docker compose down

echo "✅ Todo fue apagado correctamente."
