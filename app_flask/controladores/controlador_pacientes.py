from flask import render_template, redirect, request, session, flash
from app_flask import app
from app_flask.modelos.modelo_pacientes import Paciente
from app_flask.modelos.modelo_clientes import Cliente

@app.route('/pacientes', methods=['GET'])
def listar_pacientes():
    if 'id_administrador' not in session:
        return redirect('/')

    busqueda = request.args.get('busqueda', '').strip()

    if busqueda != '':
        pacientes = Paciente.buscar({
            'busqueda': '%' + busqueda + '%'
        })
    else:
        pacientes = Paciente.obtener_todos()

    return render_template(
        'pacientes/index.html',
        pacientes=pacientes,
        busqueda=busqueda
    )

@app.route('/pacientes/nuevo', methods=['GET'])
def formulario_nuevo_paciente():
    if 'id_administrador' not in session:
        return redirect('/')

    clientes = Cliente.obtener_todos()

    return render_template(
        'pacientes/nuevo.html',
        clientes=clientes
    )

@app.route('/pacientes/crear', methods=['POST'])
def crear_paciente():
    if 'id_administrador' not in session:
        return redirect('/')

    datos_paciente = {
        'id_cliente': request.form.get(
            'id_cliente',
            ''
        ).strip(),

        'nombre': request.form.get(
            'nombre',
            ''
        ).strip(),

        'raza': request.form.get(
            'raza',
            ''
        ).strip(),

        'edad': request.form.get(
            'edad',
            ''
        ).strip(),

        'especie': request.form.get(
            'especie',
            ''
        ).strip(),

        'sexo': request.form.get(
            'sexo',
            ''
        ).strip(),

        'historia_clinica': request.form.get(
            'historia_clinica',
            ''
        ).strip(),

        'inicio_problema': (
            request.form.get(
                'inicio_problema',
                ''
            ).strip()
            or None
        ),

        'diagnostico_vet': request.form.get(
            'diagnostico_vet',
            ''
        ).strip()
    }

    if not Paciente.validar(datos_paciente):
        return redirect('/pacientes/nuevo')

    id_paciente = Paciente.crear_uno(datos_paciente)

    if id_paciente is False:
        flash(
            'No se pudo crear el paciente.',
            'error_paciente'
        )
        return redirect('/pacientes/nuevo')

    flash(
        'Paciente registrado correctamente.',
        'exito'
    )

    return redirect(f'/pacientes/{id_paciente}')

@app.route('/pacientes/<int:id_paciente>', methods=['GET'])
def detalle_paciente(id_paciente):
    if 'id_administrador' not in session:
        return redirect('/')

    paciente = Paciente.obtener_uno_completo({
        'id_paciente': id_paciente
    })

    if paciente is None:
        return redirect('/pacientes')

    return render_template(
        'pacientes/detalle.html',
        paciente=paciente
    )

@app.route('/pacientes/<int:id_paciente>/editar', methods=['GET'])
def formulario_editar_paciente(id_paciente):
    if 'id_administrador' not in session:
        return redirect('/')

    paciente = Paciente.obtener_por_id({
        'id_paciente': id_paciente
    })

    clientes = Cliente.obtener_todos()

    if paciente is None:
        return redirect('/pacientes')

    return render_template(
        'pacientes/editar.html',
        paciente=paciente,
        clientes=clientes
    )

@app.route(
    '/pacientes/<int:id_paciente>/actualizar',
    methods=['POST']
)
def actualizar_paciente(id_paciente):
    if 'id_administrador' not in session:
        return redirect('/')

    datos = {
        'id_paciente': id_paciente,

        'id_cliente': request.form.get(
            'id_cliente',
            ''
        ).strip(),

        'nombre': request.form.get(
            'nombre',
            ''
        ).strip(),

        'raza': request.form.get(
            'raza',
            ''
        ).strip(),

        'edad': request.form.get(
            'edad',
            ''
        ).strip(),

        'especie': request.form.get(
            'especie',
            ''
        ).strip(),

        'sexo': request.form.get(
            'sexo',
            ''
        ).strip(),

        'historia_clinica': request.form.get(
            'historia_clinica',
            ''
        ).strip(),

        'inicio_problema': (
            request.form.get(
                'inicio_problema',
                ''
            ).strip()
            or None
        ),

        'diagnostico_vet': request.form.get(
            'diagnostico_vet',
            ''
        ).strip()
    }

    if not Paciente.validar(datos):
        return redirect(
            f'/pacientes/{id_paciente}/editar'
        )

    resultado = Paciente.editar_uno(datos)

    if resultado is False:
        flash(
            'No se pudo actualizar el paciente.',
            'error_paciente'
        )

        return redirect(
            f'/pacientes/{id_paciente}/editar'
        )

    flash(
        'Paciente actualizado correctamente.',
        'exito'
    )

    return redirect(
        f'/pacientes/{id_paciente}'
    )

@app.route('/pacientes/<int:id_paciente>/eliminar', methods=['POST'])
def eliminar_paciente(id_paciente):
    if 'id_administrador' not in session:
        return redirect('/')

    Paciente.eliminar_uno({
        'id_paciente': id_paciente
    })

    return redirect('/pacientes')