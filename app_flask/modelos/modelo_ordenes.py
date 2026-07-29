from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_pacientes
from app_flask.modelos import modelo_clientes
from app_flask.modelos import modelo_orden_servicios
from app_flask.modelos import modelo_orden_productos
from flask import flash
from app_flask import BASE_DATOS


class Orden:
    def __init__(self, datos):
        self.id_orden = datos['id_orden']
        self.id_paciente = datos['id_paciente']
        self.nombre_comprador = datos['nombre_comprador']
        self.estado = datos['estado']
        self.total = datos['total']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']
        self.saldo_aplicado = datos['saldo_aplicado']
        self.monto_pagado = datos['monto_pagado']
        self.estado_pago = datos['estado_pago']

        self.paciente = None
        self.orden_servicios = []
        self.orden_productos = []

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO ordenes(
                    id_paciente,
                    nombre_comprador,
                    estado,
                    total,
                    saldo_aplicado,
                    monto_pagado,
                    estado_pago
                )
                VALUES(
                    %(id_paciente)s,
                    %(nombre_comprador)s,
                    'pendiente',
                    %(total)s,
                    %(saldo_aplicado)s,
                    %(monto_pagado)s,
                    %(estado_pago)s
                );
                """

        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM ordenes
                WHERE id_orden = %(id_orden)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_todas(cls):
        query = """
                SELECT *
                FROM ordenes
                ORDER BY fecha_creacion DESC;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        ordenes = []

        for fila in resultados:
            ordenes.append(cls(fila))

        return ordenes

    @classmethod
    def obtener_por_paciente(cls, datos):
        query = """
                SELECT *
                FROM ordenes
                WHERE id_paciente = %(id_paciente)s
                ORDER BY fecha_creacion DESC;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        ordenes = []

        for fila in resultados:
            ordenes.append(cls(fila))

        return ordenes

    @classmethod
    def obtener_uno_con_paciente(cls, datos):
        query = """
                SELECT
                    ordenes.*,

                    pacientes.id_paciente AS paciente_id_paciente,
                    pacientes.nombre AS paciente_nombre,
                    pacientes.raza AS paciente_raza,
                    pacientes.edad AS paciente_edad,
                    pacientes.especie AS paciente_especie,
                    pacientes.sexo AS paciente_sexo,
                    pacientes.historia_clinica AS paciente_historia_clinica,
                    pacientes.inicio_problema AS paciente_inicio_problema,
                    pacientes.diagnostico_vet AS paciente_diagnostico_vet,
                    pacientes.id_cliente AS paciente_id_cliente,
                    pacientes.fecha_creacion AS paciente_fecha_creacion,
                    pacientes.fecha_actualizacion AS paciente_fecha_actualizacion,
                    pacientes.fecha_nacimiento AS paciente_fecha_nacimiento,

                    clientes.id_cliente AS cliente_id_cliente,
                    clientes.nombre AS cliente_nombre,
                    clientes.correo AS cliente_correo,
                    clientes.telefono AS cliente_telefono,
                    clientes.saldo AS cliente_saldo,
                    clientes.fecha_creacion AS cliente_fecha_creacion,
                    clientes.fecha_actualizacion AS cliente_fecha_actualizacion

                FROM ordenes
                LEFT JOIN pacientes
                    ON ordenes.id_paciente = pacientes.id_paciente
                LEFT JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente
                WHERE ordenes.id_orden = %(id_orden)s;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultado is False or len(resultado) < 1:
            return None

        fila = resultado[0]
        orden = cls(fila)

        if fila["paciente_id_paciente"] is not None:
            datos_paciente = {
                "id_paciente": fila["paciente_id_paciente"],
                "nombre": fila["paciente_nombre"],
                "raza": fila["paciente_raza"],
                "edad": fila["paciente_edad"],
                "especie": fila["paciente_especie"],
                "sexo": fila["paciente_sexo"],
                "historia_clinica": fila["paciente_historia_clinica"],
                "inicio_problema": fila["paciente_inicio_problema"],
                "fecha_nacimiento": fila["paciente_fecha_nacimiento"],
                "diagnostico_vet": fila["paciente_diagnostico_vet"],
                "id_cliente": fila["paciente_id_cliente"],
                "fecha_creacion": fila["paciente_fecha_creacion"],
                "fecha_actualizacion": fila["paciente_fecha_actualizacion"]
            }

            paciente = modelo_pacientes.Paciente(datos_paciente)

            if fila["cliente_id_cliente"] is not None:
                datos_cliente = {
                    "id_cliente": fila["cliente_id_cliente"],
                    "nombre": fila["cliente_nombre"],
                    "correo": fila["cliente_correo"],
                    "telefono": fila["cliente_telefono"],
                    "saldo": fila["cliente_saldo"],
                    "fecha_creacion": fila["cliente_fecha_creacion"],
                    "fecha_actualizacion": fila["cliente_fecha_actualizacion"]
                }

                paciente.cliente = modelo_clientes.Cliente(datos_cliente)

            orden.paciente = paciente

        return orden

    @classmethod
    def obtener_uno_con_servicios(cls, datos):
        query = """
                SELECT *
                FROM ordenes
                LEFT JOIN orden_servicios
                    ON ordenes.id_orden = orden_servicios.id_orden
                WHERE ordenes.id_orden = %(id_orden)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        orden = cls(resultado[0])

        for fila in resultado:
            if fila["orden_servicios.id_orden_servicio"] is not None:
                orden_servicio = {
                    "id_orden_servicio": fila["orden_servicios.id_orden_servicio"],
                    "id_orden": fila["orden_servicios.id_orden"],
                    "id_servicio": fila["id_servicio"],
                    "cantidad": fila["cantidad"],
                    "precio_unitario": fila["precio_unitario"],
                    "subtotal": fila["subtotal"],
                    "fecha_creacion": fila["orden_servicios.fecha_creacion"]
                }

                orden.orden_servicios.append(
                    modelo_orden_servicios.OrdenServicio(orden_servicio)
                )

        return orden

    @classmethod
    def obtener_uno_con_productos(cls, datos):
        query = """
                SELECT *
                FROM ordenes
                LEFT JOIN orden_productos
                    ON ordenes.id_orden = orden_productos.id_orden
                WHERE ordenes.id_orden = %(id_orden)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        orden = cls(resultado[0])

        for fila in resultado:
            if fila["orden_productos.id_orden_producto"] is not None:
                orden_producto = {
                    "id_orden_producto": fila["orden_productos.id_orden_producto"],
                    "id_orden": fila["orden_productos.id_orden"],
                    "id_producto": fila["id_producto"],
                    "cantidad": fila["cantidad"],
                    "precio_unitario": fila["precio_unitario"],
                    "subtotal": fila["subtotal"],
                    "fecha_creacion": fila["orden_productos.fecha_creacion"]
                }

                orden.orden_productos.append(
                    modelo_orden_productos.OrdenProducto(orden_producto)
                )

        return orden

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE ordenes
                SET id_paciente = %(id_paciente)s,
                    nombre_comprador = %(nombre_comprador)s,
                    estado = %(estado)s,
                    total = %(total)s
                WHERE id_orden = %(id_orden)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def actualizar_estado(cls, datos):
        query = """
                UPDATE ordenes
                SET estado = %(estado)s
                WHERE id_orden = %(id_orden)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def recalcular_total(cls, datos):
        query = """
                UPDATE ordenes
                SET total = (
                    SELECT COALESCE(SUM(subtotal), 0)
                    FROM (
                        SELECT subtotal
                        FROM orden_servicios
                        WHERE id_orden = %(id_orden)s

                        UNION ALL

                        SELECT subtotal
                        FROM orden_productos
                        WHERE id_orden = %(id_orden)s
                    ) AS detalles
                )
                WHERE id_orden = %(id_orden)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM ordenes
                WHERE id_orden = %(id_orden)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def actualizar_total(cls, datos):
        query = """
                UPDATE ordenes
                SET total = %(total)s
                WHERE id_orden = %(id_orden)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_todas_con_paciente_cliente(cls):
        query = """
                SELECT
                    ordenes.*,

                    pacientes.id_paciente AS paciente_id,
                    pacientes.nombre AS paciente_nombre,

                    clientes.id_cliente AS cliente_id,
                    clientes.nombre AS cliente_nombre

                FROM ordenes

                LEFT JOIN pacientes
                    ON ordenes.id_paciente = pacientes.id_paciente

                LEFT JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente

                ORDER BY ordenes.fecha_creacion DESC;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        if resultados is False:
            return []

        ordenes = []

        for fila in resultados:
            orden = cls(fila)

            # Propiedades adicionales para el listado.
            orden.id_cliente = fila['cliente_id']
            orden.cliente_nombre = fila['cliente_nombre']
            orden.paciente_nombre = fila['paciente_nombre']

            ordenes.append(orden)

        return ordenes

    @classmethod
    def actualizar_resumen_pago(cls, datos):
        query = """
                UPDATE ordenes
                SET monto_pagado = %(monto_pagado)s,
                    estado_pago = %(estado_pago)s,
                    estado = CASE
                        WHEN %(estado_pago)s = 'pagada'
                            THEN 'pagada'
                        ELSE estado
                    END
                WHERE id_orden = %(id_orden)s;
                """

        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def actualizar_saldo_aplicado(cls, datos):
        query = """
                UPDATE ordenes
                SET saldo_aplicado = %(saldo_aplicado)s,
                    estado_pago = %(estado_pago)s,
                    estado = CASE
                        WHEN %(estado_pago)s = 'pagada'
                            THEN 'pagada'
                        ELSE estado
                    END
                WHERE id_orden = %(id_orden)s;
                """

        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_todas_filtradas(cls, datos):
        query = """
                SELECT
                    ordenes.*,

                    pacientes.id_paciente AS paciente_id,
                    pacientes.nombre AS paciente_nombre,

                    clientes.id_cliente AS cliente_id,
                    clientes.nombre AS cliente_nombre

                FROM ordenes

                LEFT JOIN pacientes
                    ON ordenes.id_paciente = pacientes.id_paciente

                LEFT JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente

                WHERE (
                    %(cliente)s = ''
                    OR clientes.nombre LIKE %(cliente_busqueda)s
                )

                AND (
                    %(paciente)s = ''
                    OR pacientes.nombre LIKE %(paciente_busqueda)s
                )

                AND (
                    %(estado)s = ''
                    OR ordenes.estado = %(estado)s
                )

                ORDER BY ordenes.fecha_creacion DESC;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(
            query,
            datos
        )

        if resultados is False:
            return []

        ordenes = []

        for fila in resultados:
            orden = cls(fila)

            orden.id_cliente = fila['cliente_id']
            orden.cliente_nombre = fila['cliente_nombre']
            orden.paciente_nombre = fila['paciente_nombre']

            ordenes.append(orden)

        return ordenes

    @staticmethod
    def validar(datos):
        es_valido = True

        id_paciente = datos.get('id_paciente', '')
        nombre_comprador = datos.get(
            'nombre_comprador',
            ''
        )

        tiene_paciente = (
            str(id_paciente).strip() != ''
            and str(id_paciente).isdigit()
        )

        tiene_comprador = (
            isinstance(nombre_comprador, str)
            and len(nombre_comprador.strip()) >= 2
        )

        if not tiene_paciente and not tiene_comprador:
            flash(
                (
                    'Debes seleccionar un paciente o escribir '
                    'el nombre del comprador.'
                ),
                'error_orden'
            )
            es_valido = False

        # Solo se permiten estados operativos.
        if 'estado' in datos:
            estados_validos = [
                'pendiente',
                'cancelada',
                'pagada'
            ]

            if datos['estado'] not in estados_validos:
                flash(
                    'El estado de la orden no es válido.',
                    'error_estado'
                )
                es_valido = False

        return es_valido

    def saldo_pendiente(self):
        pendiente = (
            float(self.total)
            - float(self.saldo_aplicado)
            - float(self.monto_pagado)
        )

        return max(pendiente, 0)