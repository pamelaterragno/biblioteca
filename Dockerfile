FROM python:3.10-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar solo requirements primero (mejor uso de cache)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Luego copiar el resto del proyecto
COPY . .

# Comando por defecto
CMD ["streamlit", "run", "app.py"]
