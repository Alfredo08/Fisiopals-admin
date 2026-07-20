from app_flask.config.mysqlconnection import connectToMySQL
from app_flask import BASE_DATOS


class MovimientoCaja:
    def __init__(self, datos):
        self.id_pago = datos['id_pago']
        self.id_orden = datos['id_orden']
        self.monto = datos['monto']
        self.metodo_pago = datos['metodo_pago']
        self.fecha_pago = datos['fecha_pago']

        self.total_orden = datos['total_orden']
        self.monto_pagado = datos['monto_pagado']
        self.saldo_aplicado = datos['saldo_aplicado']
        self.estado_pago = datos['estado_pago']

        self.id_paciente = datos['id_paciente']
        self.nombre_paciente = datos['nombre_paciente']

        self.id_cliente = datos['id_cliente']
        self.nombre_cliente = datos['nombre_cliente']

        self.nombre_comprador = datos['nombre_comprador']

    @classmethod
    def obtener_por_fecha(cls, datos):
        query = """
                SELECT
                    pagos_orden.id_pago AS id_pago,
                    pagos_orden.id_orden AS id_orden,
                    pagos_orden.monto AS monto,
                    pagos_orden.metodo_pago AS metodo_pago,
                    pagos_orden.fecha_pago AS fecha_pago,

                    ordenes.total AS total_orden,
                    ordenes.monto_pagado AS monto_pagado,
                    ordenes.saldo_aplicado AS saldo_aplicado,
                    ordenes.estado_pago AS estado_pago,
                    ordenes.nombre_comprador AS nombre_comprador,

                    pacientes.id_paciente AS id_paciente,
                    pacientes.nombre AS nombre_paciente,

                    clientes.id_cliente AS id_cliente,
                    clientes.nombre AS nombre_cliente

                FROM pagos_orden

                JOIN ordenes
                    ON pagos_orden.id_orden = ordenes.id_orden

                LEFT JOIN pacientes
                    ON ordenes.id_paciente = pacientes.id_paciente

                LEFT JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente

                WHERE DATE(pagos_orden.fecha_pago) = %(fecha)s

                ORDER BY pagos_orden.fecha_pago DESC;
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

                FROM pagos_orden

                WHERE DATE(fecha_pago) = %(fecha)s;
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