from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

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
# FORMULARIO DE EDICIÓN DE ORDEN
# =========================================================

@app.route('/ordenes/<int:id_orden>/editar', methods=['GET'])
def formulario_editar_orden(id_orden):
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

    pacientes = Paciente.obtener_todos_con_cliente()
    servicios = Servicio.obtener_todos()
    productos = Producto.obtener_todos()

    servicios_orden = OrdenServicio.obtener_por_orden({
        'id_orden': id_orden
    })

    productos_orden = OrdenProducto.obtener_por_orden({
        'id_orden': id_orden
    })

    cantidades_servicios = {}

    for item in servicios_orden:
        cantidades_servicios[item.id_servicio] = (
            cantidades_servicios.get(item.id_servicio, 0)
            + int(item.cantidad)
        )

    cantidades_productos = {}

    for item in productos_orden:
        cantidades_productos[item.id_producto] = (
            cantidades_productos.get(item.id_producto, 0)
            + int(item.cantidad)
        )

    return render_template(
        'ordenes/editar.html',
        orden=orden,
        pacientes=pacientes,
        servicios=servicios,
        productos=productos,
        cantidades_servicios=cantidades_servicios,
        cantidades_productos=cantidades_productos
    )


# =========================================================
# GUARDAR EDICIÓN DE ORDEN
# =========================================================

@app.route('/ordenes/<int:id_orden>/editar', methods=['POST'])
def editar_orden(id_orden):
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

    id_paciente_formulario = request.form.get(
        'id_paciente',
        ''
    ).strip()

    nombre_comprador = request.form.get(
        'nombre_comprador',
        ''
    ).strip()

    datos_validacion = {
        'id_paciente': id_paciente_formulario,
        'nombre_comprador': nombre_comprador,
        'estado': orden.estado
    }

    if not Orden.validar(datos_validacion):
        return redirect(f'/ordenes/{id_orden}/editar')

    id_paciente_nuevo = (
        int(id_paciente_formulario)
        if id_paciente_formulario
        else None
    )

    nombre_comprador_nuevo = (
        nombre_comprador
        if nombre_comprador
        else None
    )

    # -----------------------------------------------------
    # Obtener detalle actual
    # -----------------------------------------------------

    servicios_actuales = OrdenServicio.obtener_por_orden({
        'id_orden': id_orden
    })

    productos_actuales = OrdenProducto.obtener_por_orden({
        'id_orden': id_orden
    })

    servicios_anteriores = {}

    for item in servicios_actuales:
        servicios_anteriores[item.id_servicio] = (
            servicios_anteriores.get(item.id_servicio, 0)
            + int(item.cantidad)
        )

    productos_anteriores = {}

    for item in productos_actuales:
        productos_anteriores[item.id_producto] = (
            productos_anteriores.get(item.id_producto, 0)
            + int(item.cantidad)
        )

    # -----------------------------------------------------
    # Leer cantidades de servicios
    # -----------------------------------------------------

    ids_servicios = request.form.getlist('id_servicio')
    cantidades_servicios = request.form.getlist(
        'cantidad_servicio'
    )

    servicios_nuevos = {}

    for id_servicio, cantidad_texto in zip(
        ids_servicios,
        cantidades_servicios
    ):
        try:
            cantidad = int(cantidad_texto or 0)
        except (TypeError, ValueError):
            flash(
                'Una de las cantidades de servicios no es válida.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        if cantidad < 0:
            flash(
                'Las cantidades no pueden ser negativas.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        try:
            id_servicio_entero = int(id_servicio)
        except (TypeError, ValueError):
            flash(
                'Uno de los servicios seleccionados no es válido.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        servicios_nuevos[id_servicio_entero] = cantidad

    # -----------------------------------------------------
    # Leer cantidades de productos
    # -----------------------------------------------------

    ids_productos = request.form.getlist('id_producto')
    cantidades_productos = request.form.getlist(
        'cantidad_producto'
    )

    productos_nuevos = {}

    for id_producto, cantidad_texto in zip(
        ids_productos,
        cantidades_productos
    ):
        try:
            cantidad = int(cantidad_texto or 0)
        except (TypeError, ValueError):
            flash(
                'Una de las cantidades de productos no es válida.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        if cantidad < 0:
            flash(
                'Las cantidades no pueden ser negativas.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        # Una línea de producto con cantidad 0 no debe llegar nunca
        # a orden_productos. Se interpreta como eliminación.

        try:
            id_producto_entero = int(id_producto)
        except (TypeError, ValueError):
            flash(
                'Uno de los productos seleccionados no es válido.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        productos_nuevos[id_producto_entero] = cantidad

    # -----------------------------------------------------
    # Validar que exista al menos un detalle
    # -----------------------------------------------------

    hay_servicios = any(
        cantidad > 0
        for cantidad in servicios_nuevos.values()
    )

    hay_productos = any(
        cantidad > 0
        for cantidad in productos_nuevos.values()
    )

    if not hay_servicios and not hay_productos:
        flash(
            'La orden debe incluir al menos un servicio o producto.',
            'error_orden'
        )
        return redirect(f'/ordenes/{id_orden}/editar')

    # -----------------------------------------------------
    # Validar servicios y calcular total
    # -----------------------------------------------------

    datos_servicios_nuevos = {}
    total_servicios = Decimal('0.00')

    for id_servicio, cantidad in servicios_nuevos.items():
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
            return redirect(f'/ordenes/{id_orden}/editar')

        cantidad_anterior = servicios_anteriores.get(
            id_servicio,
            0
        )

        # Si el servicio ya estaba en la orden, conservamos
        # el precio histórico de esa línea.
        precio_unitario = None

        for item in servicios_actuales:
            if item.id_servicio == id_servicio:
                precio_unitario = Decimal(
                    str(item.precio_unitario)
                )
                break

        if precio_unitario is None:
            precio_unitario = Decimal(
                str(servicio.precio)
            )

        subtotal = precio_unitario * cantidad

        datos_servicios_nuevos[id_servicio] = {
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal,
            'cantidad_anterior': cantidad_anterior
        }

        total_servicios += subtotal

    # -----------------------------------------------------
    # Validar productos, stock y calcular total
    # -----------------------------------------------------

    datos_productos_nuevos = {}
    total_productos = Decimal('0.00')

    for id_producto, cantidad in productos_nuevos.items():
        # Cantidad 0 significa que el producto se elimina de la orden.
        # Nunca se debe ejecutar INSERT/UPDATE con cantidad 0 porque la
        # tabla orden_productos tiene restricciones CHECK.
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
            return redirect(f'/ordenes/{id_orden}/editar')

        cantidad_anterior = productos_anteriores.get(
            id_producto,
            0
        )

        stock_disponible_para_edicion = (
            int(producto.stock) + cantidad_anterior
        )

        if cantidad > stock_disponible_para_edicion:
            flash(
                (
                    f'No hay stock suficiente para {producto.nombre}. '
                    f'Disponible para esta edición: '
                    f'{stock_disponible_para_edicion}.'
                ),
                'error_stock'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        precio_unitario = None

        for item in productos_actuales:
            if item.id_producto == id_producto:
                precio_unitario = Decimal(str(item.precio_unitario))
                break

        if precio_unitario is None:
            precio_unitario = Decimal(str(producto.precio))

        # Normalizar valores monetarios a 2 decimales antes de enviarlos
        # a MySQL. Esto evita discrepancias con CHECK de subtotal/precio.
        precio_unitario = precio_unitario.quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        subtotal = (precio_unitario * Decimal(cantidad)).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

        if cantidad <= 0 or precio_unitario < 0 or subtotal < 0:
            flash(
                f'Los datos del producto {producto.nombre} no son válidos.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        datos_productos_nuevos[id_producto] = {
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal,
            'cantidad_anterior': cantidad_anterior
        }

        total_productos += subtotal

    total_nuevo = total_servicios + total_productos

    # -----------------------------------------------------
    # Ajustar saldo aplicado si cambia el cliente o si el
    # nuevo total ya no soporta todo el saldo aplicado.
    # -----------------------------------------------------

    cliente_anterior_id = None

    if (
        orden.paciente is not None
        and orden.paciente.cliente is not None
    ):
        cliente_anterior_id = orden.paciente.cliente.id_cliente

    cliente_nuevo_id = None

    if id_paciente_nuevo is not None:
        paciente_nuevo = Paciente.obtener_por_id({
            'id_paciente': id_paciente_nuevo
        })

        if paciente_nuevo is None:
            flash(
                'El paciente seleccionado no existe.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        cliente_nuevo_id = paciente_nuevo.id_cliente

    saldo_aplicado_anterior = Decimal(
        str(orden.saldo_aplicado)
    )

    saldo_aplicado_nuevo = saldo_aplicado_anterior

    # Si se cambia de cliente, devolvemos el saldo al cliente
    # original y no lo aplicamos automáticamente al nuevo cliente.
    if cliente_anterior_id != cliente_nuevo_id:
        if (
            cliente_anterior_id is not None
            and saldo_aplicado_anterior > 0
        ):
            Cliente.agregar_saldo({
                'id_cliente': cliente_anterior_id,
                'monto': saldo_aplicado_anterior
            })

        saldo_aplicado_nuevo = Decimal('0.00')

    # Si el total bajó por debajo del saldo aplicado, devolvemos
    # la diferencia al cliente.
    elif saldo_aplicado_nuevo > total_nuevo:
        diferencia = saldo_aplicado_nuevo - total_nuevo

        if cliente_anterior_id is not None:
            Cliente.agregar_saldo({
                'id_cliente': cliente_anterior_id,
                'monto': diferencia
            })

        saldo_aplicado_nuevo = total_nuevo

    # -----------------------------------------------------
    # Actualizar servicios
    # -----------------------------------------------------

    for item in servicios_actuales:
        datos_nuevo = datos_servicios_nuevos.get(
            item.id_servicio
        )

        if datos_nuevo is None:
            resultado = OrdenServicio.eliminar_uno({
                'id_orden_servicio': item.id_orden_servicio
            })

            if resultado is False:
                flash(
                    'No se pudo eliminar uno de los servicios.',
                    'error_orden'
                )
                return redirect(f'/ordenes/{id_orden}/editar')

            continue

        resultado = OrdenServicio.editar_uno({
            'id_orden_servicio': item.id_orden_servicio,
            'id_servicio': item.id_servicio,
            'cantidad': datos_nuevo['cantidad'],
            'precio_unitario': datos_nuevo['precio_unitario'],
            'subtotal': datos_nuevo['subtotal']
        })

        if resultado is False:
            flash(
                'No se pudo actualizar uno de los servicios.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

    ids_servicios_existentes = {
        item.id_servicio
        for item in servicios_actuales
    }

    for id_servicio, datos_nuevo in datos_servicios_nuevos.items():
        if id_servicio in ids_servicios_existentes:
            continue

        resultado = OrdenServicio.crear_uno({
            'id_orden': id_orden,
            'id_servicio': id_servicio,
            'cantidad': datos_nuevo['cantidad'],
            'precio_unitario': datos_nuevo['precio_unitario'],
            'subtotal': datos_nuevo['subtotal']
        })

        if resultado is False:
            flash(
                'No se pudo agregar uno de los servicios.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

    # -----------------------------------------------------
    # Actualizar productos e inventario por diferencia
    # -----------------------------------------------------

    # Primero modificamos las líneas de la orden. La cantidad 0 ya fue
    # descartada arriba y por tanto nunca llega a orden_productos.
    ajustes_stock = []

    for item in productos_actuales:
        datos_nuevo = datos_productos_nuevos.get(item.id_producto)

        cantidad_anterior = int(item.cantidad)
        cantidad_nueva = (
            int(datos_nuevo['cantidad'])
            if datos_nuevo is not None
            else 0
        )

        diferencia = cantidad_nueva - cantidad_anterior

        if datos_nuevo is None:
            resultado = OrdenProducto.eliminar_uno({
                'id_orden_producto': item.id_orden_producto
            })
        else:
            resultado = OrdenProducto.editar_uno({
                'id_orden_producto': item.id_orden_producto,
                'id_producto': item.id_producto,
                'cantidad': cantidad_nueva,
                'precio_unitario': datos_nuevo['precio_unitario'],
                'subtotal': datos_nuevo['subtotal']
            })

        if resultado is False:
            flash(
                (
                    f'No se pudo guardar el producto de la orden '
                    f'({item.id_producto}). No se modificó el stock.'
                ),
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        if diferencia != 0:
            ajustes_stock.append({
                'id_producto': item.id_producto,
                'diferencia': diferencia
            })

    ids_productos_existentes = {
        item.id_producto
        for item in productos_actuales
    }

    for id_producto, datos_nuevo in datos_productos_nuevos.items():
        if id_producto in ids_productos_existentes:
            continue

        resultado = OrdenProducto.crear_uno({
            'id_orden': id_orden,
            'id_producto': id_producto,
            'cantidad': int(datos_nuevo['cantidad']),
            'precio_unitario': datos_nuevo['precio_unitario'],
            'subtotal': datos_nuevo['subtotal']
        })

        if resultado is False:
            flash(
                f'No se pudo agregar el producto {id_producto} a la orden.',
                'error_orden'
            )
            return redirect(f'/ordenes/{id_orden}/editar')

        ajustes_stock.append({
            'id_producto': id_producto,
            'diferencia': int(datos_nuevo['cantidad'])
        })

    # El inventario se ajusta después de que la línea de la orden fue
    # guardada correctamente. Así evitamos descontar stock si MySQL
    # rechaza la operación.
    for ajuste in ajustes_stock:
        if ajuste['diferencia'] > 0:
            Producto.disminuir_stock({
                'id_producto': ajuste['id_producto'],
                'cantidad': ajuste['diferencia']
            })
        elif ajuste['diferencia'] < 0:
            Producto.aumentar_stock({
                'id_producto': ajuste['id_producto'],
                'cantidad': abs(ajuste['diferencia'])
            })

    # -----------------------------------------------------
    # Guardar datos generales de la orden
    # -----------------------------------------------------

    resultado = Orden.editar_uno({
        'id_orden': id_orden,
        'id_paciente': id_paciente_nuevo,
        'nombre_comprador': nombre_comprador_nuevo,
        'estado': orden.estado,
        'total': total_nuevo
    })

    if resultado is False:
        flash(
            'No se pudieron guardar los datos generales de la orden.',
            'error_orden'
        )
        return redirect(f'/ordenes/{id_orden}/editar')

    # -----------------------------------------------------
    # Recalcular pagos sin modificar el historial
    # -----------------------------------------------------

    total_pagado = Decimal(str(
        PagoOrden.obtener_total_pagado({
            'id_orden': id_orden
        })
    ))

    total_cubierto = (
        saldo_aplicado_nuevo
        + total_pagado
    )

    if total_cubierto >= total_nuevo:
        estado_pago = 'pagada'
    elif total_cubierto > 0:
        estado_pago = 'parcial'
    else:
        estado_pago = 'pendiente'

    resultado = Orden.actualizar_resumen_pago_edicion({
        'id_orden': id_orden,
        'total': total_nuevo,
        'monto_pagado': total_pagado,
        'saldo_aplicado': saldo_aplicado_nuevo,
        'estado_pago': estado_pago
    })

    if resultado is False:
        flash(
            'La orden fue modificada, pero no se pudo actualizar su estado de pago.',
            'error_orden'
        )
        return redirect(f'/ordenes/{id_orden}')

    flash(
        'La orden fue actualizada correctamente.',
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