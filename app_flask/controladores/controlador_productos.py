from flask import render_template, redirect, request, session, flash
from app_flask import app
from app_flask.modelos.modelo_productos import Producto

@app.route('/productos', methods=['GET'])
def listar_productos():
    if 'id_administrador' not in session:
        return redirect('/')

    busqueda = request.args.get('busqueda', '').strip()

    if busqueda != '':
        productos = Producto.buscar({
            'busqueda': '%' + busqueda + '%'
        })
    else:
        productos = Producto.obtener_todos()

    return render_template(
        'productos/index.html',
        productos=productos,
        busqueda=busqueda
    )

@app.route('/productos/nuevo', methods=['GET'])
def formulario_nuevo_producto():
    if 'id_administrador' not in session:
        return redirect('/')

    return render_template('productos/nuevo.html')

@app.route('/productos/crear', methods=['POST'])
def crear_producto():
    if 'id_administrador' not in session:
        return redirect('/')

    if not Producto.validar(request.form):
        return redirect('/productos/nuevo')

    Producto.crear_uno(request.form)

    return redirect('/productos')

@app.route('/productos/<int:id_producto>', methods=['GET'])
def detalle_producto(id_producto):
    if 'id_administrador' not in session:
        return redirect('/')

    producto = Producto.obtener_por_id({
        'id_producto': id_producto
    })

    if producto is None:
        return redirect('/productos')

    return render_template(
        'productos/detalle.html',
        producto=producto
    )

@app.route('/productos/<int:id_producto>/editar', methods=['GET'])
def formulario_editar_producto(id_producto):
    if 'id_administrador' not in session:
        return redirect('/')

    if not session.get(
            'puede_gestionar_catalogo',
            False
        ):
            flash(
                (
                    'No tienes permiso para modificar '
                    'los datos de los productos existentes.'
                ),
                'error_permiso'
            )
            return redirect(
                f'/productos/{id_producto}'
            )

    producto = Producto.obtener_por_id({
        'id_producto': id_producto
    })

    if producto is None:
        return redirect('/productos')

    return render_template(
        'productos/editar.html',
        producto=producto
    )

@app.route(
    '/productos/<int:id_producto>/actualizar',
    methods=['POST']
)
def actualizar_producto(id_producto):
    if 'id_administrador' not in session:
        return redirect('/')
    
    if not session.get(
        'puede_gestionar_catalogo',
        False
    ):
        flash(
            (
                'No tienes permiso para modificar '
                'los datos de los productos existentes.'
            ),
            'error_permiso'
        )
        return redirect(
            f'/productos/{id_producto}'
        )

    producto_actual = Producto.obtener_por_id({
        'id_producto': id_producto
    })

    if producto_actual is None:
        flash(
            'El producto no existe.',
            'error_producto'
        )
        return redirect('/productos')

    datos = {
        'id_producto': id_producto,
        'nombre': request.form.get(
            'nombre',
            ''
        ).strip(),
        'precio': request.form.get(
            'precio',
            ''
        ).strip(),

        # Por defecto conserva el stock actual.
        'stock': producto_actual.stock
    }

    if session.get(
        'puede_gestionar_catalogo',
        False
    ):
        datos['stock'] = request.form.get(
            'stock',
            ''
        ).strip()

    if not Producto.validar(datos):
        return redirect(
            f'/productos/{id_producto}/editar'
        )

    Producto.editar_uno(datos)

    flash(
        'Producto actualizado correctamente.',
        'exito'
    )

    return redirect(
        f'/productos/{id_producto}'
    )

@app.route(
    '/productos/<int:id_producto>/eliminar',
    methods=['POST']
)
def eliminar_producto(id_producto):
    if 'id_administrador' not in session:
        return redirect('/')

    if not session.get(
        'puede_gestionar_catalogo',
        False
    ):
        flash(
            'No tienes permiso para eliminar productos.',
            'error_permiso'
        )
        return redirect(
            f'/productos/{id_producto}'
        )

    producto = Producto.obtener_por_id({
        'id_producto': id_producto
    })

    if producto is None:
        flash(
            'El producto no existe.',
            'error_producto'
        )
        return redirect('/productos')

    resultado = Producto.eliminar_uno({
        'id_producto': id_producto
    })

    if resultado is False:
        flash(
            'No se pudo eliminar el producto.',
            'error_producto'
        )
        return redirect(
            f'/productos/{id_producto}'
        )

    flash(
        'Producto eliminado correctamente.',
        'exito'
    )

    return redirect('/productos')