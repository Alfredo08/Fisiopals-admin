from flask import render_template, redirect, request, session, flash
from app_flask import app
from app_flask.modelos.modelo_servicios import Servicio

@app.route('/servicios', methods=['GET'])
def listar_servicios():
    if 'id_administrador' not in session:
        return redirect('/')

    busqueda = request.args.get('busqueda', '').strip()

    if busqueda != '':
        servicios = Servicio.buscar({
            'busqueda': '%' + busqueda + '%'
        })
    else:
        servicios = Servicio.obtener_todos()

    return render_template(
        'servicios/index.html',
        servicios=servicios,
        busqueda=busqueda
    )

@app.route('/servicios/nuevo', methods=['GET'])
def formulario_nuevo_servicio():
    if 'id_administrador' not in session:
        return redirect('/')

    return render_template('servicios/nuevo.html')

@app.route('/servicios/crear', methods=['POST'])
def crear_servicio():
    if 'id_administrador' not in session:
        return redirect('/')

    if not Servicio.validar(request.form):
        return redirect('/servicios/nuevo')

    Servicio.crear_uno(request.form)

    return redirect('/servicios')

@app.route('/servicios/<int:id_servicio>', methods=['GET'])
def detalle_servicio(id_servicio):
    if 'id_administrador' not in session:
        return redirect('/')

    servicio = Servicio.obtener_por_id({
        'id_servicio': id_servicio
    })

    if servicio is None:
        return redirect('/servicios')

    return render_template(
        'servicios/detalle.html',
        servicio=servicio
    )

@app.route('/servicios/<int:id_servicio>/editar')
def formulario_editar_servicio(id_servicio):
    if 'id_administrador' not in session:
        return redirect('/')

    if not session.get(
        'puede_gestionar_catalogo',
        False
    ):
        flash(
            (
                'No tienes permiso para editar '
                'precios de servicios.'
            ),
            'error_permiso'
        )
        return redirect(
            f'/servicios/{id_servicio}'
        )

    servicio = Servicio.obtener_por_id({
        'id_servicio': id_servicio
    })

    return render_template(
        'servicios/editar.html',
        servicio=servicio
    )

@app.route('/servicios/<int:id_servicio>/actualizar', methods=['POST'])
def actualizar_servicio(id_servicio):
    if 'id_administrador' not in session:
        return redirect('/')

    if not session.get(
        'puede_gestionar_catalogo',
        False
    ):
        flash(
            (
                'No tienes permiso para modificar '
                'los datos de los servicios existentes.'
            ),
            'error_permiso'
        )
        return redirect(
            f'/servicios/{id_servicio}'
        )

    if not Servicio.validar(request.form):
        return redirect(f'/servicios/{id_servicio}/editar')

    datos = {
        **request.form,
        'id_servicio': id_servicio
    }

    Servicio.editar_uno(datos)

    return redirect(f'/servicios/{id_servicio}')

@app.route(
    '/servicios/<int:id_servicio>/eliminar',
    methods=['POST']
)
def eliminar_servicio(id_servicio):
    if 'id_administrador' not in session:
        return redirect('/')

    if not session.get(
        'puede_gestionar_catalogo',
        False
    ):
        flash(
            'No tienes permiso para eliminar servicios.',
            'error_permiso'
        )
        return redirect(
            f'/servicios/{id_servicio}'
        )

    servicio = Servicio.obtener_por_id({
        'id_servicio': id_servicio
    })

    if servicio is None:
        flash(
            'El servicio no existe.',
            'error_servicio'
        )
        return redirect('/servicios')

    resultado = Servicio.eliminar_uno({
        'id_servicio': id_servicio
    })

    if resultado is False:
        flash(
            'No se pudo eliminar el servicio.',
            'error_servicio'
        )
        return redirect(
            f'/servicios/{id_servicio}'
        )

    flash(
        'Servicio eliminado correctamente.',
        'exito'
    )

    return redirect('/servicios')