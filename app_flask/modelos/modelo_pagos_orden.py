from app_flask.config.mysqlconnection import connectToMySQL
from flask import flash
from app_flask import BASE_DATOS


class PagoOrden:
    def __init__(self, datos):
        self.id_pago = datos['id_pago']
        self.id_orden = datos['id_orden']
        self.monto = datos['monto']
        self.metodo_pago = datos['metodo_pago']
        self.fecha_pago = datos['fecha_pago']
        self.fecha_creacion = datos['fecha_creacion']

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO pagos_orden(
                    id_orden,
                    monto,
                    metodo_pago
                )
                VALUES(
                    %(id_orden)s,
                    %(monto)s,
                    %(metodo_pago)s
                );
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_orden(cls, datos):
        query = """
                SELECT *
                FROM pagos_orden
                WHERE id_orden = %(id_orden)s
                ORDER BY fecha_pago DESC;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultados is False:
            return []

        pagos = []

        for fila in resultados:
            pagos.append(cls(fila))

        return pagos

    @classmethod
    def obtener_total_pagado(cls, datos):
        query = """
                SELECT COALESCE(SUM(monto), 0) AS total_pagado
                FROM pagos_orden
                WHERE id_orden = %(id_orden)s;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultado is False or len(resultado) < 1:
            return 0

        return resultado[0]['total_pagado']

    @staticmethod
    def validar(datos):
        es_valido = True

        try:
            monto = float(datos.get('monto', 0))

            if monto <= 0:
                flash(
                    'El abono debe ser mayor a cero.',
                    'error_abono'
                )
                es_valido = False

        except (TypeError, ValueError):
            flash(
                'El monto del abono no es válido.',
                'error_abono'
            )
            es_valido = False

        metodos_validos = ['efectivo', 'transferencia']

        if datos.get('metodo_pago') not in metodos_validos:
            flash(
                'Selecciona un método de pago válido.',
                'error_metodo_pago'
            )
            es_valido = False

        return es_valido