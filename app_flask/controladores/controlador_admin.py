from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt

from app_flask import app
from app_flask.modelos.modelo_administradores import Administrador

bcrypt = Bcrypt(app)

@app.route('/', methods=['GET'])
def despliega_login():
    if 'id_administrador' in session:
        return redirect('/dashboard')

    return render_template('login.html')

@app.route('/procesa/login', methods=['POST'])
def procesa_login():
    administrador = Administrador.obtener_por_correo({
        'correo': request.form['correo']
    })

    if administrador is None:
        flash('Correo o contraseña incorrectos.', 'error_login')
        return redirect('/')

    if not bcrypt.check_password_hash(
        administrador.password,
        request.form['password']
    ):
        flash('Correo o contraseña incorrectos.', 'error_login')
        return redirect('/')

    session['id_administrador'] = administrador.id_administrador
    session['nombre_administrador'] = administrador.nombre_completo

    return redirect('/dashboard')

@app.route('/dashboard', methods=['GET'])
def despliega_dashboard():
    if 'id_administrador' not in session:
        return redirect('/')

    return render_template('dashboard.html')

@app.route('/procesa/logout', methods=['POST'])
def procesa_logout():
    session.clear()
    return redirect('/')

@app.route('/admins/nuevo', methods=['GET'])
def formulario_nuevo_admin():
    return render_template('administradores/nuevo.html')

@app.route('/admins/crear', methods=['POST'])
def crear_admin():
    if not Administrador.validar(request.form):
        return redirect('/admins/nuevo')

    admin_existente = Administrador.obtener_por_correo({
        'correo': request.form['correo']
    })

    if admin_existente is not None:
        flash('Este correo ya está registrado.', 'error_correo')
        return redirect('/admins/nuevo')

    password_encriptado = bcrypt.generate_password_hash(
        request.form['password']
    )

    datos = {
        'nombre_completo': request.form['nombre_completo'],
        'correo': request.form['correo'],
        'password': password_encriptado
    }

    id_administrador = Administrador.crear_uno(datos)

    session['id_administrador'] = id_administrador
    session['nombre_administrador'] = datos['nombre_completo']

    return redirect('/dashboard')