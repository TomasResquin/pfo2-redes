import sqlite3
from flask import Flask, request, jsonify, session
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

# Configuracion del servidor
HOST = "localhost"
PORT = 5000
DB_NAME = "tareas.db"

app = Flask(__name__)
# Clave para firmar la cookie de sesion
app.secret_key = "pfo2-programacion-sobre-redes"


def inicializar_db():
    # Creacion de la base de datos y la tabla de usuarios
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena_hash TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.")
        return True
    except sqlite3.Error as e:
        print(f"Error: No se pudo acceder a la base de datos ({e}).")
        return False


def obtener_credenciales():
    # Leer usuario y contraseña del JSON recibido
    datos = request.get_json(silent=True) or {}
    usuario = str(datos.get("usuario", "")).strip()
    contrasena = str(datos.get("contraseña", ""))
    return usuario, contrasena


@app.route('/registro', methods=['POST'])
def registro():
    usuario, contrasena = obtener_credenciales()
    if not usuario or not contrasena:
        return jsonify({"error": "Se requieren usuario y contraseña"}), 400

    # Hashear la contraseña antes de guardarla (nunca en texto plano)
    contrasena_hash = generate_password_hash(contrasena)

    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute(
            "INSERT INTO usuarios (usuario, contrasena_hash) VALUES (?, ?)",
            (usuario, contrasena_hash)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 409
    finally:
        conn.close()

    print(f"Usuario registrado: {usuario}")
    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201


@app.route('/login', methods=['POST'])
def login():
    usuario, contrasena = obtener_credenciales()

    conn = sqlite3.connect(DB_NAME)
    fila = conn.execute(
        "SELECT contrasena_hash FROM usuarios WHERE usuario = ?", (usuario,)
    ).fetchone()
    conn.close()

    # Comparar la contraseña recibida con el hash guardado
    if fila is None or not check_password_hash(fila[0], contrasena):
        return jsonify({"error": "Credenciales invalidas"}), 401

    # Guardar el usuario en la sesion para permitir el acceso a /tareas
    session["usuario"] = usuario
    print(f"Inicio de sesion: {usuario}")
    return jsonify({"mensaje": "Inicio de sesion exitoso"}), 200


@app.route('/tareas', methods=['GET'])
def tareas():
    # Solo se permite el acceso si el usuario inicio sesion
    if "usuario" not in session:
        return jsonify({"error": "Debe iniciar sesion primero"}), 401

    usuario = escape(session["usuario"])
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Tareas</title></head>
<body style="font-family: Consolas, monospace; background: #EAE0D5; color: #3B2F2F; padding: 2rem;">
    <h1 style="border-bottom: 2px solid #5C4033;">Bienvenido, {usuario}</h1>
    <p>Accediste al sistema de gestion de tareas.</p>
</body>
</html>"""


if __name__ == '__main__':
    if inicializar_db():
        app.run(host=HOST, port=PORT)
