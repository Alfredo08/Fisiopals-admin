from flask import render_template, redirect, request, session
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

    producto = Producto.obtener_por_id({
        'id_producto': id_producto
    })

    if producto is None:
        return redirect('/productos')

    return render_template(
        'productos/editar.html',
        producto=producto
    )

@app.route('/productos/<int:id_producto>/actualizar', methods=['POST'])
def actualizar_producto(id_producto):
    if 'id_administrador' not in session:
        return redirect('/')

    if not Producto.validar(request.form):
        return redirect(f'/productos/{id_producto}/editar')

    datos = {
        **request.form,
        'id_producto': id_producto
    }

    Producto.editar_uno(datos)

    return redirect(f'/productos/{id_producto}')

@app.route('/productos/<int:id_producto>/eliminar', methods=['POST'])
def eliminar_producto(id_producto):
    if 'id_administrador' not in session:
        return redirect('/')

    Producto.eliminar_uno({
        'id_producto': id_producto
    })

    return redirect('/productos')