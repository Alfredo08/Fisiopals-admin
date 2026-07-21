from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt

from app_flask import app
from app_flask.modelos.modelo_administradores import Administrador


bcrypt = Bcrypt(app)


# =========================================================
# LOGIN
# =========================================================

@app.route('/', methods=['GET'])
def despliega_login():
    if 'id_administrador' in session:
        return redirect('/dashboard')

    return render_template('login.html')


@app.route('/procesa/login', methods=['POST'])
def procesa_login():
    nombre_usuario = request.form.get(
        'nombre_usuario',
        ''
    ).strip()

    password = request.form.get(
        'password',
        ''
    )

    administrador = Administrador.obtener_por_nombre_usuario({
        'nombre_usuario': nombre_usuario
    })

    if administrador is None:
        flash(
            'Usuario o contraseña incorrectos.',
            'error_login'
        )
        return redirect('/')

    if not bcrypt.check_password_hash(
        administrador.password,
        password
    ):
        flash(
            'Usuario o contraseña incorrectos.',
            'error_login'
        )
        return redirect('/')

    session['id_administrador'] = (
        administrador.id_administrador
    )

    session['nombre_administrador'] = (
        administrador.nombre_completo
    )

    session['nombre_usuario'] = (
        administrador.nombre_usuario
    )

    session['puede_gestionar_catalogo'] = (
        administrador.puede_gestionar_catalogo
    )

    return redirect('/dashboard')


# =========================================================
# DASHBOARD
# =========================================================

@app.route('/dashboard', methods=['GET'])
def despliega_dashboard():
    if 'id_administrador' not in session:
        return redirect('/')

    return render_template('dashboard.html')


# =========================================================
# LOGOUT
# =========================================================

@app.route('/procesa/logout', methods=['POST'])
def procesa_logout():
    session.clear()

    return redirect('/')


# =========================================================
# FORMULARIO DE NUEVO ADMINISTRADOR
# =========================================================

@app.route('/admins/nuevo', methods=['GET'])
def formulario_nuevo_admin():
    # Mantén o elimina esta validación según quién pueda
    # registrar nuevos administradores.
    if 'id_administrador' not in session:
        return redirect('/')

    return render_template(
        'administradores/nuevo.html'
    )


# =========================================================
# CREAR ADMINISTRADOR
# =========================================================

@app.route('/admins/crear', methods=['POST'])
def crear_admin():
    if 'id_administrador' not in session:
        return redirect('/')

    datos_validacion = {
        'nombre_completo': request.form.get(
            'nombre_completo',
            ''
        ).strip(),

        'nombre_usuario': request.form.get(
            'nombre_usuario',
            ''
        ).strip(),

        'password': request.form.get(
            'password',
            ''
        ),

        'password_confirmar': request.form.get(
            'password_confirmar',
            ''
        )
    }

    if not Administrador.validar(datos_validacion):
        return redirect('/admins/nuevo')

    administrador_existente = (
        Administrador.obtener_por_nombre_usuario({
            'nombre_usuario': (
                datos_validacion['nombre_usuario']
            )
        })
    )

    if administrador_existente is not None:
        flash(
            'Ese nombre de usuario ya está registrado.',
            'error_nombre_usuario'
        )
        return redirect('/admins/nuevo')

    password_encriptado = (
        bcrypt.generate_password_hash(
            datos_validacion['password']
        ).decode('utf-8')
    )

    datos_admin = {
        'nombre_completo': (
            datos_validacion['nombre_completo']
        ),

        'nombre_usuario': (
            datos_validacion['nombre_usuario']
        ),

        'password': password_encriptado
    }

    id_administrador = Administrador.crear_uno(
        datos_admin
    )

    if id_administrador is False:
        flash(
            'No se pudo crear el administrador.',
            'error_admin'
        )
        return redirect('/admins/nuevo')

    flash(
        'Administrador creado correctamente.',
        'exito'
    )

    return redirect('/dashboard')