# 📚 Mi Biblioteca Personal

Aplicación web desarrollada con **Streamlit + PostgreSQL** para registrar, visualizar y analizar libros leídos.

---

## 🚀 Cómo iniciar el entorno

1. Cloná el proyecto:
   ```bash
   git clone https://github.com/tuusuario/streamlit_libros.git
   cd streamlit_libros
   ```

2. Iniciá el entorno:
   ```bash
   ./iniciar.sh start
   ```

3. Accedé desde el navegador a:
   ```
   http://localhost:8501
   ```

> 💡 El entorno también levanta un contenedor de PostgreSQL automáticamente con tus datos.

---

## ⚙️ Requisitos

- Docker + Docker Compose
- VS Code (opcional)
- Python 3.10+ (si lo corrés fuera de Docker)

---

## 🧱 Estructura del proyecto

```
📁 streamlit_libros/
├── app.py                   # Interfaz principal de Streamlit
├── agregar_campos_libros.py # Consulta datos a OpenLibrary
├── mostrar_estadisticas.py  # Muestra estadísticas gráficas
├── libros.csv               # Dataset inicial
├── iniciar.sh               # Script para iniciar el entorno
├── docker-compose.yml       # Configuración de servicios
├── Dockerfile               # Imagen personalizada
├── requirements.txt         # Dependencias del proyecto
└── backup_scripts/          # Scripts antiguos no utilizados
```

---

## 📦 Instalación manual (sin Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## ✨ Funcionalidades

- Agregar libros y completarlos automáticamente con OpenLibrary
- Filtrar y buscar libros
- Ver estadísticas de lectura
- Marcar libros como leídos o pendientes de compra
- Eliminar libros de forma interactiva
