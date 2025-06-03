# 📚 Mi Biblioteca Personal

Una aplicación web para gestionar tu colección de libros de forma personalizada.

## 🚀 Características principales

- **Registro y Login de Usuarios**:
  - Cada usuario crea su cuenta y gestiona su propia biblioteca de libros.
  - Autenticación segura con contraseñas encriptadas.

- **Gestión Personalizada de Libros**:
  - Cada usuario tiene acceso solo a su lista de libros.
  - Agrega libros manualmente o con autocompletado de datos desde la Google Books API.

- **Autocompletado Inteligente**:
  - Al ingresar título (y opcionalmente autor), la app completa automáticamente:
    - Título oficial
    - Autor/es
    - Año de publicación
    - ISBN
    - Editorial
    - Idioma

- **Prevención de Duplicados**:
  - La aplicación valida que no existan libros repetidos (título + autor) por usuario.

- **Estadísticas Personalizadas**:
  - Cada usuario puede visualizar estadísticas sobre sus propios libros:
    - Total de libros
    - Promedio de puntuación
    - Estado de lectura
    - Autores más leídos
    - Distribución de puntuaciones

- **Interfaz Limpia y Sencilla**:
  - Formularios de carga optimizados.
  - Experiencia de usuario mejorada.

- **Arquitectura Modular**:
  - Conexiones a base de datos centralizadas en un módulo `db.py` para mayor mantenibilidad.

## ⚙️ Tecnologías utilizadas

- Python 3
- Streamlit
- PostgreSQL
- SQLAlchemy
- psycopg2
- Google Books API
- Plotly (para visualizaciones)

## 🚀 Cómo ejecutar

1. Clona este repositorio:
    ```bash
    git clone https://github.com/tu_usuario/tu_repositorio.git
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3. Corre la app:
    ```bash
    streamlit run app.py
    ```

4. Asegúrate de tener PostgreSQL corriendo y las variables de entorno configuradas:
    ```env
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=biblioteca
    DB_USER=tu_usuario
    DB_PASS=tu_contraseña
    ```

## 📝 Mejoras recientes

"Mejoras en sistema de usuarios y personalización de la biblioteca:
- Implementación de registro y login de usuarios con autenticación segura.
- Personalización completa de la experiencia: cada usuario gestiona su propia lista de libros y estadísticas.
- Autocompletado inteligente de título, autor, año, editorial, idioma e ISBN usando Google Books API al agregar un libro.
- Validación para evitar duplicados: no permite registrar el mismo título y autor para un mismo usuario.
- Estadísticas personalizadas: solo se muestran los datos del usuario logueado.
- Refactorización de la conexión a base de datos mediante módulo db.py para mayor eficiencia y mantenimiento."
