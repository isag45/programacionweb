from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la clave secreta
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave_secreta_por_defecto')

# Simulación de base de datos
usuarios = {}
apuestas = []

# Datos de ejemplo
partidos = [
    {'id': 1, 'equipo_a': 'Argentina', 'equipo_b': 'Brasil', 'fecha': '2024-11-10'},
    {'id': 2, 'equipo_a': 'Francia', 'equipo_b': 'España', 'fecha': '2024-11-12'},
    {'id': 3, 'equipo_a': 'Alemania', 'equipo_b': 'Inglaterra', 'fecha': '2024-11-14'},
    {'id': 4, 'equipo_a': 'Italia', 'equipo_b': 'Portugal', 'fecha': '2024-11-16'},
    {'id': 5, 'equipo_a': 'México', 'equipo_b': 'Uruguay', 'fecha': '2024-11-18'},
    {'id': 6, 'equipo_a': 'Japón', 'equipo_b': 'Corea del Sur', 'fecha': '2024-11-20'}
]

equipos = [
    {'nombre': 'Argentina', 'grupo': 'A'},
    {'nombre': 'Brasil', 'grupo': 'A'},
    {'nombre': 'Francia', 'grupo': 'B'},
    {'nombre': 'España', 'grupo': 'B'},
    {'nombre': 'Alemania', 'grupo': 'C'},
    {'nombre': 'Inglaterra', 'grupo': 'C'},
    {'nombre': 'Italia', 'grupo': 'D'},
    {'nombre': 'Portugal', 'grupo': 'D'},
    {'nombre': 'México', 'grupo': 'E'},
    {'nombre': 'Uruguay', 'grupo': 'E'},
    {'nombre': 'Japón', 'grupo': 'F'},
    {'nombre': 'Corea del Sur', 'grupo': 'F'}
]

# Middleware para verificar si el usuario está logueado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de la aplicación

@app.route('/')
def index():
    """Página principal con los partidos disponibles"""
    usuario = session.get('usuario')
    return render_template('index.html', partidos=partidos, usuario=usuario)

@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    """Formulario para crear un nuevo usuario"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validar campos
        if not nombre or not email or not password:
            flash('Por favor, completa todos los campos', 'error')
            return redirect(url_for('crear_usuario'))

        # Validar si el email ya está registrado
        if email in usuarios:
            flash('El email ya está registrado', 'error')
            return redirect(url_for('crear_usuario'))

        # Guardar usuario con contraseña hasheada
        usuarios[email] = {
            'nombre': nombre,
            'password': generate_password_hash(password),
            'apuestas': []
        }

        flash('Usuario creado exitosamente. Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('crear_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Formulario de inicio de sesión"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = usuarios.get(email)
        if usuario and check_password_hash(usuario['password'], password):
            session['usuario'] = usuario['nombre']
            session['email'] = email
            flash(f'Bienvenido, {usuario["nombre"]}!', 'success')
            return redirect(url_for('index'))
        
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/equipos')
@login_required
def mostrar_equipos():
    """Mostrar todos los equipos disponibles"""
    return render_template('equipos.html', equipos=equipos)

@app.route('/apuesta/<int:partido_id>', methods=['GET', 'POST'])
@login_required
def hacer_apuesta(partido_id):
    """Formulario para hacer una apuesta en un partido específico"""
    partido = next((p for p in partidos if p['id'] == partido_id), None)
    
    if not partido:
        flash('Partido no encontrado', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        goles_a = request.form.get('goles_a', type=int)
        goles_b = request.form.get('goles_b', type=int)
        
        if goles_a is None or goles_b is None:
            flash('Por favor ingresa un número válido de goles', 'error')
            return render_template('hacer_apuesta.html', partido=partido)

        email = session['email']
        apuesta = {
            'partido_id': partido_id,
            'goles_equipo_a': goles_a,
            'goles_equipo_b': goles_b,
            'fecha': partido['fecha']
        }
        
        usuarios[email]['apuestas'].append(apuesta)
        flash(f'Apuesta realizada exitosamente para {partido["equipo_a"]} vs {partido["equipo_b"]}', 'success')
        return redirect(url_for('index'))

    return render_template('hacer_apuesta.html', partido=partido)

@app.route('/mis_apuestas')
@login_required
def mis_apuestas():
    """Ver todas las apuestas realizadas por el usuario"""
    email = session['email']
    usuario = usuarios[email]
    return render_template('mis_apuestas.html', apuestas=usuario['apuestas'], partidos=partidos)

if __name__ == '__main__':
    app.run(debug=True)
