from app_flask.config.mysqlconnection import connectToMySQL
from app_flask import BASE_DATOS


class MovimientoCaja:
    def __init__(self, datos):
        self.tipo_movimiento = datos['tipo_movimiento']
        self.id_movimiento = datos['id_movimiento']

        self.id_orden = datos['id_orden']
        self.id_cliente = datos['id_cliente']
        self.id_paciente = datos['id_paciente']

        self.nombre_cliente = datos['nombre_cliente']
        self.nombre_paciente = datos['nombre_paciente']
        self.nombre_comprador = datos['nombre_comprador']

        self.monto = datos['monto']
        self.metodo_pago = datos['metodo_pago']
        self.fecha_movimiento = datos['fecha_movimiento']

        self.total_orden = datos['total_orden']
        self.monto_pagado = datos['monto_pagado']
        self.saldo_aplicado = datos['saldo_aplicado']
        self.estado_pago = datos['estado_pago']

    @classmethod
    def obtener_por_fecha(cls, datos):
        query = """
                SELECT
                    'pago_orden' AS tipo_movimiento,
                    pagos_orden.id_pago AS id_movimiento,

                    pagos_orden.id_orden AS id_orden,

                    clientes.id_cliente AS id_cliente,
                    pacientes.id_paciente AS id_paciente,

                    clientes.nombre AS nombre_cliente,
                    pacientes.nombre AS nombre_paciente,
                    ordenes.nombre_comprador AS nombre_comprador,

                    pagos_orden.monto AS monto,
                    pagos_orden.metodo_pago AS metodo_pago,
                    pagos_orden.fecha_pago AS fecha_movimiento,

                    ordenes.total AS total_orden,
                    ordenes.monto_pagado AS monto_pagado,
                    ordenes.saldo_aplicado AS saldo_aplicado,
                    ordenes.estado_pago AS estado_pago

                FROM pagos_orden

                JOIN ordenes
                    ON pagos_orden.id_orden = ordenes.id_orden

                LEFT JOIN pacientes
                    ON ordenes.id_paciente = pacientes.id_paciente

                LEFT JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente

                WHERE DATE(pagos_orden.fecha_pago) = %(fecha)s

                UNION ALL

                SELECT
                    'abono_cliente' AS tipo_movimiento,
                    abonos_clientes.id_abono_cliente AS id_movimiento,

                    NULL AS id_orden,

                    clientes.id_cliente AS id_cliente,
                    NULL AS id_paciente,

                    clientes.nombre AS nombre_cliente,
                    NULL AS nombre_paciente,
                    NULL AS nombre_comprador,

                    abonos_clientes.monto AS monto,
                    abonos_clientes.metodo_pago AS metodo_pago,
                    abonos_clientes.fecha_abono AS fecha_movimiento,

                    NULL AS total_orden,
                    NULL AS monto_pagado,
                    NULL AS saldo_aplicado,
                    NULL AS estado_pago

                FROM abonos_clientes

                JOIN clientes
                    ON abonos_clientes.id_cliente = clientes.id_cliente

                WHERE DATE(abonos_clientes.fecha_abono) = %(fecha)s

                ORDER BY fecha_movimiento DESC;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(
            query,
            datos
        )

        if resultados is False:
            return []

        movimientos = []

        for fila in resultados:
            movimientos.append(cls(fila))

        return movimientos

    @classmethod
    def obtener_totales_por_fecha(cls, datos):
        query = """
                SELECT
                    COALESCE(SUM(monto), 0) AS total_general,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN metodo_pago = 'efectivo'
                                THEN monto
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total_efectivo,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN metodo_pago = 'transferencia'
                                THEN monto
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total_transferencia,

                    COUNT(*) AS cantidad_movimientos

                FROM (
                    SELECT
                        monto,
                        metodo_pago,
                        fecha_pago AS fecha_movimiento

                    FROM pagos_orden

                    UNION ALL

                    SELECT
                        monto,
                        metodo_pago,
                        fecha_abono AS fecha_movimiento

                    FROM abonos_clientes
                ) AS movimientos

                WHERE DATE(fecha_movimiento) = %(fecha)s;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            datos
        )

        if resultado is False or len(resultado) < 1:
            return {
                'total_general': 0,
                'total_efectivo': 0,
                'total_transferencia': 0,
                'cantidad_movimientos': 0
            }

        return resultado[0]
    
class AplicacionSaldo:
    def __init__(self, datos):
        self.id_orden = datos['id_orden']
        self.fecha_aplicacion = datos['fecha_aplicacion']
        self.saldo_aplicado = datos['saldo_aplicado']
        self.total_orden = datos['total_orden']
        self.estado_pago = datos['estado_pago']

        self.id_paciente = datos['id_paciente']
        self.nombre_paciente = datos['nombre_paciente']

        self.id_cliente = datos['id_cliente']
        self.nombre_cliente = datos['nombre_cliente']

    @classmethod
    def obtener_por_fecha(cls, datos):
        query = """
                SELECT
                    ordenes.id_orden AS id_orden,
                    ordenes.fecha_creacion AS fecha_aplicacion,
                    ordenes.saldo_aplicado AS saldo_aplicado,
                    ordenes.total AS total_orden,
                    ordenes.estado_pago AS estado_pago,

                    pacientes.id_paciente AS id_paciente,
                    pacientes.nombre AS nombre_paciente,

                    clientes.id_cliente AS id_cliente,
                    clientes.nombre AS nombre_cliente

                FROM ordenes

                JOIN pacientes
                    ON ordenes.id_paciente = pacientes.id_paciente

                JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente

                WHERE ordenes.saldo_aplicado > 0
                  AND DATE(ordenes.fecha_creacion) = %(fecha)s

                ORDER BY ordenes.fecha_creacion DESC;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(
            query,
            datos
        )

        if resultados is False:
            return []

        aplicaciones = []

        for fila in resultados:
            aplicaciones.append(cls(fila))

        return aplicaciones