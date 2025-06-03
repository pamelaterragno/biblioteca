import streamlit as st
import bcrypt
from db import conectar_db

# Registrar nuevo usuario
def registrar_usuario(username, password):
    conn = conectar_db()
    cur = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# Validar login de usuario
def validar_usuario(username, password):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT password FROM usuarios WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        hashed_password = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return "ok"
        else:
            return "wrong_password"
    else:
        return "user_not_found"

# Obtener ID de usuario
def obtener_id_usuario(username):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return user_id

# Mostrar libros del usuario
def mostrar_libros(usuario_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT titulo, autor FROM libros WHERE usuario_id = %s", (usuario_id,))
    libros = cur.fetchall()
    cur.close()
    conn.close()
    st.subheader("Tus libros:")
    for libro in libros:
        st.write(f"- {libro[0]} por {libro[1]}")


# Login y Registro
def login_y_registro():
    if "usuario" in st.session_state:
        # Ya hay sesión activa, redirigir a app principal
        st.rerun()

    st.title("Biblioteca con Usuarios")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Ingresar"):
            resultado = validar_usuario(username, password)
            if resultado == "ok":
                st.session_state["usuario"] = username
                st.success(f"Bienvenido {username}")
                st.rerun()  # Redirige a la app
            elif resultado == "wrong_password":
                st.error("Contraseña incorrecta.")
            elif resultado == "user_not_found":
                st.error("Usuario no registrado. Por favor regístrese.")

    with col2:
        if st.button("Registrarse"):
            if username and password:
                if registrar_usuario(username, password):
                    st.success("Usuario registrado con éxito. Ahora podés iniciar sesión.")
                else:
                    st.error("El usuario ya existe. Elija otro nombre.")
            else:
                st.warning("Debe ingresar usuario y contraseña para registrarse.")


# Logout
def logout():
    if st.sidebar.button("Cerrar sesión"):
        del st.session_state["usuario"]
        st.rerun()

# App principal
def app_principal():
    usuario = st.session_state["usuario"]
    st.sidebar.write(f"Sesión iniciada como: {usuario}")
    logout()
    usuario_id = obtener_id_usuario(usuario)
    mostrar_libros(usuario_id)