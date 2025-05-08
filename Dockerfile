# Imagen base liviana de Python
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivo de dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos al contenedor
COPY . .

# Exponer el puerto donde corre Streamlit
EXPOSE 8501

# Comando que lanza la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
