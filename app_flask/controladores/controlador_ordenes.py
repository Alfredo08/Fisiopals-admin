from decimal import Decimal, InvalidOperation

from flask import render_template, redirect, request, session, flash

from app_flask import app
from app_flask.modelos.modelo_ordenes import Orden
from app_flask.modelos.modelo_pacientes import Paciente
from app_flask.modelos.modelo_clientes import Cliente
from app_flask.modelos.modelo_servicios import Servicio
from app_flask.modelos.modelo_productos import Producto
from app_flask.modelos.modelo_orden_servicios import OrdenServicio
from app_flask.modelos.modelo_orden_productos import OrdenProducto
from app_flask.modelos.modelo_pagos_orden import PagoOrden


# =========================================================
# LISTADO DE ÓRDENES
# =========================================================

@app.route('/ordenes', methods=['GET'])
@app.route('/ordenes', methods=['GET'])
def listar_ordenes():
    if 'id_administrador' not in session:
        return redirect('/')

    cliente = request.args.get(
        'cliente',
        ''
    ).strip()

    paciente = request.args.get(
        'paciente',
        ''
    ).strip()

    estado = request.args.get(
        'estado',
        ''
    ).strip()

    estados_validos = [
        '',
        'pendiente',
        'pagada',
        'cancelada'
    ]

    if estado not in estados_validos:
        estado = ''

    datos_filtro = {
        'cliente': cliente,
        'cliente_busqueda': f'%{cliente}%',

        'paciente': paciente,
        'paciente_busqueda': f'%{paciente}%',

        'estado': estado
    }

    ordenes = Orden.obtener_todas_filtradas(
        datos_filtro
    )

    return render_template(
        'ordenes/index.html',
        ordenes=ordenes,
        cliente_filtro=cliente,
        paciente_filtro=paciente,
        estado_filtro=estado
    )


# =========================================================
# FORMULARIO DE NUEVA ORDEN
# =========================================================

@app.route('/ordenes/nueva', methods=['GET'])
def formulario_nueva_orden():
    if 'id_administrador' not in session:
        return redirect('/')

    pacientes = Paciente.obtener_todos_con_cliente()
    servicios = Servicio.obtener_todos()
    productos = Producto.obtener_todos()

    return render_template(
        'ordenes/nueva.html',
        pacientes=pacientes,
        servicios=servicios,
        productos=productos
    )


# =========================================================
# CREAR ORDEN
# =========================================================

@app.route('/ordenes/crear', methods=['POST'])
def crear_orden():
    if 'id_administrador' not in session:
        return redirect('/')

    id_paciente_formulario = request.form.get('id_paciente', '').strip()
    nombre_comprador = request.form.get(
        'nombre_comprador',
        ''
    ).strip()

    datos_validacion = {
        'id_paciente': id_paciente_formulario,
        'nombre_comprador': nombre_comprador,
        'estado': 'pendiente'
    }

    if not Orden.validar(datos_validacion):
        return redirect('/ordenes/nueva')

    id_paciente = (
        int(id_paciente_formulario)
        if id_paciente_formulario
        else None
    )

    nombre_comprador = nombre_comprador or None

    # -----------------------------------------------------
    # Preparar servicios seleccionados
    # -----------------------------------------------------

    ids_servicios = request.form.getlist('id_servicio')
    cantidades_servicios = request.form.getlist(
        'cantidad_servicio'
    )

    detalles_servicios = []
    total_servicios = Decimal('0.00')

    for id_servicio, cantidad_texto in zip(
        ids_servicios,
        cantidades_servicios
    ):
        try:
            cantidad = int(cantidad_texto or 0)
        except (TypeError, ValueError):
            cantidad = 0

        if cantidad <= 0:
            continue

        servicio = Servicio.obtener_por_id({
            'id_servicio': id_servicio
        })

        if servicio is None:
            flash(
                'Uno de los servicios seleccionados no existe.',
                'error_orden'
            )
            return redirect('/ordenes/nueva')

        precio_unitario = Decimal(str(servicio.precio))
        subtotal = precio_unitario * cantidad

        detalles_servicios.append({
            'id_servicio': servicio.id_servicio,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal
        })

        total_servicios += subtotal

    # La orden debe incluir uno o más servicios.
    if len(detalles_servicios) == 0 and nombre_comprador == None:
        flash(
            'La orden debe incluir al menos un servicio.',
            'error_orden'
        )
        return redirect('/ordenes/nueva')

    # -----------------------------------------------------
    # Preparar productos seleccionados y validar stock
    # -----------------------------------------------------

    ids_productos = request.form.getlist('id_producto')
    cantidades_productos = request.form.getlist(
        'cantidad_producto'
    )

    detalles_productos = []
    total_productos = Decimal('0.00')

    for id_producto, cantidad_texto in zip(
        ids_productos,
        cantidades_productos
    ):
        try:
            cantidad = int(cantidad_texto or 0)
        except (TypeError, ValueError):
            cantidad = 0

        if cantidad <= 0:
            continue

        producto = Producto.obtener_por_id({
            'id_producto': id_producto
        })

        if producto is None:
            flash(
                'Uno de los productos seleccionados no existe.',
                'error_orden'
            )
            return redirect('/ordenes/nueva')

        if cantidad > int(producto.stock):
            flash(
                (
                    f'No hay stock suficiente para '
                    f'{producto.nombre}. '
                    f'Stock disponible: {producto.stock}.'
                ),
                'error_stock'
            )
            return redirect('/ordenes/nueva')

        precio_unitario = Decimal(str(producto.precio))
        subtotal = precio_unitario * cantidad

        detalles_productos.append({
            'id_producto': producto.id_producto,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal
        })

        total_productos += subtotal

    total_orden = total_servicios + total_productos

    # -----------------------------------------------------
    # Crear la orden inicialmente en cero
    # -----------------------------------------------------

    datos_orden = {
        'id_paciente': id_paciente,
        'nombre_comprador': nombre_comprador,
        'estado': 'pendiente',
        'total': Decimal('0.00'),
        'saldo_aplicado': Decimal('0.00'),
        'monto_pagado': Decimal('0.00'),
        'estado_pago': 'pendiente'
    }

    id_orden = Orden.crear_uno(datos_orden)

    if id_orden is False:
        flash(
            'No se pudo crear la orden.',
            'error_orden'
        )
        return redirect('/ordenes/nueva')

    # -----------------------------------------------------
    # Registrar servicios
    # -----------------------------------------------------

    for detalle in detalles_servicios:
        resultado = OrdenServicio.crear_uno({
            'id_orden': id_orden,
            **detalle
        })

        if resultado is False:
            flash(
                'No se pudo agregar uno de los servicios.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}')

    # -----------------------------------------------------
    # Registrar productos y descontar inventario
    # -----------------------------------------------------

    for detalle in detalles_productos:
        resultado = OrdenProducto.crear_uno({
            'id_orden': id_orden,
            **detalle
        })

        if resultado is False:
            flash(
                'No se pudo agregar uno de los productos.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}')

        Producto.disminuir_stock({
            'id_producto': detalle['id_producto'],
            'cantidad': detalle['cantidad']
        })

    # -----------------------------------------------------
    # Guardar total de la orden
    # -----------------------------------------------------

    Orden.actualizar_total({
        'id_orden': id_orden,
        'total': total_orden
    })

    # -----------------------------------------------------
    # Aplicar saldo a favor del cliente
    # -----------------------------------------------------

    saldo_aplicado = Decimal('0.00')
    estado_pago = 'pendiente'

    if id_paciente is not None:
        paciente = Paciente.obtener_por_id({
            'id_paciente': id_paciente
        })

        if paciente is not None:
            cliente = Cliente.obtener_por_id({
                'id_cliente': paciente.id_cliente
            })

            if cliente is not None:
                saldo_cliente = Decimal(str(cliente.saldo))

                if saldo_cliente > 0:
                    saldo_aplicado = min(
                        saldo_cliente,
                        total_orden
                    )

                    if saldo_aplicado > 0:
                        Cliente.descontar_saldo({
                            'id_cliente': cliente.id_cliente,
                            'monto': saldo_aplicado
                        })

    if saldo_aplicado >= total_orden:
        estado_pago = 'pagada'
    elif saldo_aplicado > 0:
        estado_pago = 'parcial'

    Orden.actualizar_saldo_aplicado({
        'id_orden': id_orden,
        'saldo_aplicado': saldo_aplicado,
        'estado_pago': estado_pago
    })

    flash(
        'La orden fue creada correctamente.',
        'exito'
    )

    return redirect(f'/ordenes/{id_orden}')


# =========================================================
# DETALLE DE LA ORDEN
# =========================================================

@app.route('/ordenes/<int:id_orden>', methods=['GET'])
def detalle_orden(id_orden):
    if 'id_administrador' not in session:
        return redirect('/')

    orden = Orden.obtener_uno_con_paciente({
        'id_orden': id_orden
    })

    if orden is None:
        flash(
            'La orden solicitada no existe.',
            'error_orden'
        )
        return redirect('/ordenes')

    servicios = (
        OrdenServicio.obtener_por_orden_con_servicio({
            'id_orden': id_orden
        })
    )

    productos = (
        OrdenProducto.obtener_por_orden_con_producto({
            'id_orden': id_orden
        })
    )

    pagos = PagoOrden.obtener_por_orden({
        'id_orden': id_orden
    })

    return render_template(
        'ordenes/detalle.html',
        orden=orden,
        servicios=servicios,
        productos=productos,
        pagos=pagos
    )


# =========================================================
# ACTUALIZAR ESTADO GENERAL
# =========================================================

@app.route(
    '/ordenes/<int:id_orden>/estado',
    methods=['POST']
)
def actualizar_estado_orden(id_orden):
    if 'id_administrador' not in session:
        return redirect('/')

    orden = Orden.obtener_por_id({
        'id_orden': id_orden
    })

    if orden is None:
        flash(
            'La orden no existe.',
            'error_orden'
        )
        return redirect('/ordenes')

    nuevo_estado = request.form.get(
        'estado',
        ''
    ).strip()

    estados_validos = [
        'pendiente',
        'cancelada'
    ]

    if nuevo_estado not in estados_validos:
        flash(
            (
                'El estado seleccionado no es válido. '
                'El pago se controla por separado.'
            ),
            'error_estado'
        )
        return redirect(f'/ordenes/{id_orden}')

    # Una orden pagada puede seguir pendiente operativamente.
    # No bloqueamos el estado por estado_pago.
    Orden.actualizar_estado({
        'id_orden': id_orden,
        'estado': nuevo_estado
    })

    flash(
        'El estado de la orden fue actualizado.',
        'exito'
    )

    return redirect(f'/ordenes/{id_orden}')

# =========================================================
# REGISTRAR ABONO
# =========================================================

@app.route(
    '/ordenes/<int:id_orden>/abonar',
    methods=['POST']
)
def abonar_orden(id_orden):
    if 'id_administrador' not in session:
        return redirect('/')

    orden = Orden.obtener_uno_con_paciente({
        'id_orden': id_orden
    })

    if orden is None:
        flash(
            'La orden no existe.',
            'error_orden'
        )
        return redirect('/ordenes')

    if orden.estado == 'cancelada':
        flash(
            'No se pueden registrar pagos en una orden cancelada.',
            'error_abono'
        )
        return redirect(f'/ordenes/{id_orden}')

    if orden.estado_pago == 'pagada':
        flash(
            'Esta orden ya fue pagada en su totalidad.',
            'error_abono'
        )
        return redirect(f'/ordenes/{id_orden}')

    datos_pago = {
        'id_orden': id_orden,
        'monto': request.form.get('monto', '').strip(),
        'metodo_pago': request.form.get(
            'metodo_pago',
            ''
        ).strip()
    }

    if not PagoOrden.validar(datos_pago):
        return redirect(f'/ordenes/{id_orden}')

    try:
        monto = Decimal(datos_pago['monto'])
    except (InvalidOperation, TypeError, ValueError):
        flash(
            'El monto proporcionado no es válido.',
            'error_abono'
        )
        return redirect(f'/ordenes/{id_orden}')

    saldo_pendiente = Decimal(
        str(orden.saldo_pendiente())
    )

    if saldo_pendiente <= 0:
        flash(
            'Esta orden ya no tiene saldo pendiente.',
            'error_abono'
        )
        return redirect(f'/ordenes/{id_orden}')

    if monto > saldo_pendiente:
        flash(
            (
                'El abono no puede ser mayor al saldo '
                f'pendiente de ${saldo_pendiente:.2f}.'
            ),
            'error_abono'
        )
        return redirect(f'/ordenes/{id_orden}')

    id_pago = PagoOrden.crear_uno({
        'id_orden': id_orden,
        'monto': monto,
        'metodo_pago': datos_pago['metodo_pago']
    })

    if id_pago is False:
        flash(
            'No se pudo registrar el abono.',
            'error_abono'
        )
        return redirect(f'/ordenes/{id_orden}')

    total_pagado = Decimal(str(
        PagoOrden.obtener_total_pagado({
            'id_orden': id_orden
        })
    ))

    total_orden = Decimal(str(orden.total))
    saldo_aplicado = Decimal(
        str(orden.saldo_aplicado)
    )

    total_cubierto = saldo_aplicado + total_pagado

    if total_cubierto >= total_orden:
        estado_pago = 'pagada'
    elif total_cubierto > 0:
        estado_pago = 'parcial'
    else:
        estado_pago = 'pendiente'

    Orden.actualizar_resumen_pago({
        'id_orden': id_orden,
        'monto_pagado': total_pagado,
        'estado_pago': estado_pago
    })

    flash(
        'El abono fue registrado correctamente.',
        'exito'
    )

    return redirect(f'/ordenes/{id_orden}')


# =========================================================
# ELIMINAR ORDEN
# =========================================================

@app.route(
    '/ordenes/<int:id_orden>/eliminar',
    methods=['POST']
)
def eliminar_orden(id_orden):
    if 'id_administrador' not in session:
        return redirect('/')

    orden = Orden.obtener_uno_con_paciente({
        'id_orden': id_orden
    })

    if orden is None:
        flash(
            'La orden no existe.',
            'error_orden'
        )
        return redirect('/ordenes')

    pagos = PagoOrden.obtener_por_orden({
        'id_orden': id_orden
    })

    # Evita eliminar órdenes que ya tienen pagos.
    if len(pagos) > 0:
        flash(
            (
                'No se puede eliminar una orden que '
                'ya tiene pagos registrados.'
            ),
            'error_orden'
        )
        return redirect(f'/ordenes/{id_orden}')

    productos_orden = (
        OrdenProducto.obtener_por_orden_con_producto({
            'id_orden': id_orden
        })
    )

    # Restaurar inventario.
    for item in productos_orden:
        Producto.aumentar_stock({
            'id_producto': item.id_producto,
            'cantidad': item.cantidad
        })

    # Devolver al cliente el saldo aplicado.
    saldo_aplicado = Decimal(
        str(orden.saldo_aplicado)
    )

    if (
        saldo_aplicado > 0
        and orden.paciente is not None
        and orden.paciente.cliente is not None
    ):
        Cliente.agregar_saldo({
            'id_cliente': orden.paciente.cliente.id_cliente,
            'monto': saldo_aplicado
        })

    resultado = Orden.eliminar_uno({
        'id_orden': id_orden
    })

    if resultado is False:
        flash(
            'No se pudo eliminar la orden.',
            'error_orden'
        )
        return redirect(f'/ordenes/{id_orden}')

    flash(
        'La orden fue eliminada correctamente.',
        'exito'
    )

    return redirect('/ordenes')