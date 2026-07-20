from flask import render_template, redirect, request, session, flash
from app_flask import app
from app_flask.modelos.modelo_clientes import Cliente
from app_flask.modelos.modelo_pacientes import Paciente

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    if 'id_administrador' not in session:
        return redirect('/')

    busqueda = request.args.get('busqueda', '').strip()

    if busqueda != '':
        clientes = Cliente.buscar({
            'busqueda': '%' + busqueda + '%'
        })
    else:
        clientes = Cliente.obtener_todos()

    return render_template(
        'clientes/index.html',
        clientes=clientes,
        busqueda=busqueda
    )

@app.route('/clientes/nuevo', methods=['GET'])
def formulario_nuevo_cliente():
    if 'id_administrador' not in session:
        return redirect('/')

    return render_template('clientes/nuevo.html')

@app.route('/clientes/crear', methods=['POST'])
def crear_cliente():
    if 'id_administrador' not in session:
        return redirect('/')

    datos_cliente = {
        'nombre': request.form.get('nombre', '').strip(),
        'correo': request.form.get('correo', '').strip(),
        'telefono': request.form.get('telefono', '').strip()
    }

    datos_paciente = {
        'nombre': request.form.get('nombre_paciente', '').strip(),
        'raza': request.form.get('raza', '').strip(),
        'edad': request.form.get('edad', '').strip(),
        'especie': request.form.get('especie', '').strip(),
        'sexo': request.form.get('sexo', '').strip(),

        'historia_clinica': request.form.get(
            'historia_clinica',
            ''
        ).strip(),

        'inicio_problema': (
            request.form.get('inicio_problema', '').strip()
            or None
        ),

        'diagnostico_vet': request.form.get(
            'diagnostico_vet',
            ''
        ).strip()
    }

    cliente_valido = Cliente.validar(datos_cliente)

    paciente_valido = Paciente.validar({
        **datos_paciente,
        # Se usa temporalmente para pasar la validación.
        # El id real se asigna después de crear al cliente.
        'id_cliente': '1'
    })

    if not cliente_valido or not paciente_valido:
        return redirect('/clientes/nuevo')

    cliente_por_correo = Cliente.obtener_por_correo({
        'correo': datos_cliente['correo']
    })

    if cliente_por_correo is not None:
        flash(
            'Ya existe un cliente registrado con ese correo.',
            'error_correo'
        )
        return redirect('/clientes/nuevo')

    cliente_por_telefono = Cliente.obtener_por_telefono({
        'telefono': datos_cliente['telefono']
    })

    if cliente_por_telefono is not None:
        flash(
            'Ya existe un cliente registrado con ese teléfono.',
            'error_telefono'
        )
        return redirect('/clientes/nuevo')

    id_cliente = Cliente.crear_uno(datos_cliente)

    if id_cliente is False:
        flash(
            'No se pudo crear el cliente.',
            'error_cliente'
        )
        return redirect('/clientes/nuevo')

    datos_paciente['id_cliente'] = id_cliente

    id_paciente = Paciente.crear_uno(datos_paciente)

    if id_paciente is False:
        flash(
            'El cliente fue creado, pero no se pudo registrar el paciente.',
            'error_paciente'
        )
        return redirect(f'/clientes/{id_cliente}')

    flash(
        'Cliente y paciente registrados correctamente.',
        'exito'
    )

    return redirect(f'/clientes/{id_cliente}')

@app.route('/clientes/<int:id_cliente>', methods=['GET'])
def detalle_cliente(id_cliente):
    if 'id_administrador' not in session:
        return redirect('/')

    cliente = Cliente.obtener_con_pacientes({
        'id_cliente': id_cliente
    })

    if cliente is None:
        return redirect('/clientes')

    return render_template(
        'clientes/detalle.html',
        cliente=cliente
    )

@app.route('/clientes/<int:id_cliente>/editar', methods=['GET'])
def formulario_editar_cliente(id_cliente):
    if 'id_administrador' not in session:
        return redirect('/')

    cliente = Cliente.obtener_por_id({
        'id_cliente': id_cliente
    })

    if cliente is None:
        return redirect('/clientes')

    return render_template(
        'clientes/editar.html',
        cliente=cliente
    )

@app.route('/clientes/<int:id_cliente>/actualizar', methods=['POST'])
def actualizar_cliente(id_cliente):
    if 'id_administrador' not in session:
        return redirect('/')

    if not Cliente.validar(request.form):
        return redirect(f'/clientes/{id_cliente}/editar')

    datos = {
        **request.form,
        'id_cliente': id_cliente
    }

    Cliente.editar_uno(datos)

    return redirect(f'/clientes/{id_cliente}')

@app.route('/clientes/<int:id_cliente>/eliminar', methods=['POST'])
def eliminar_cliente(id_cliente):
    if 'id_administrador' not in session:
        return redirect('/')

    Cliente.eliminar_uno({
        'id_cliente': id_cliente
    })

    return redirect('/clientes')

@app.route('/clientes/<int:id_cliente>/agregar-saldo', methods=['POST'])
def agregar_saldo_cliente(id_cliente):
    if 'id_administrador' not in session:
        return redirect('/')

    monto = float(request.form['monto'])

    if monto <= 0:
        flash('El monto debe ser mayor a 0.', 'error_saldo')
        return redirect(f'/clientes/{id_cliente}')

    Cliente.agregar_saldo({
        'id_cliente': id_cliente,
        'monto': monto
    })

    return redirect(f'/clientes/{id_cliente}')
