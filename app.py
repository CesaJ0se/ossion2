from flask import Flask, render_template, request, redirect, session, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.secret_key = "clave_super_secreta"
CORS(app)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def get_db_connection():
    conn = sqlite3.connect("usuarios.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- RUTAS PRINCIPALES ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- API DE REGISTRO ---
@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if not nombre or not email or not password:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
            (nombre, email, password)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Usuario registrado correctamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El correo ya está registrado"}), 400

# --- API DE LOGIN ---
@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM usuarios WHERE email = ? AND password = ?",
        (email, password)
    ).fetchone()
    conn.close()

    if user:
        session["username"] = user["nombre"]
        session["email"] = user["email"]
        return jsonify({"message": "Login exitoso"}), 200
    else:
        return jsonify({"error": "Credenciales incorrectas"}), 401

# --- INICIALIZAR BASE DE DATOS ---
if __name__ == "__main__":
    init_db()
    app.run(debug=True)