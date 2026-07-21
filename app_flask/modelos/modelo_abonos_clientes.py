from flask import flash

from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class AbonoCliente:
    def __init__(self, datos):
        self.id_abono_cliente = datos['id_abono_cliente']
        self.id_cliente = datos['id_cliente']
        self.monto = datos['monto']
        self.metodo_pago = datos['metodo_pago']
        self.fecha_abono = datos['fecha_abono']
        self.fecha_creacion = datos['fecha_creacion']

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO abonos_clientes(
                    id_cliente,
                    monto,
                    metodo_pago
                )
                VALUES(
                    %(id_cliente)s,
                    %(monto)s,
                    %(metodo_pago)s
                );
                """

        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_cliente(cls, datos):
        query = """
                SELECT *
                FROM abonos_clientes
                WHERE id_cliente = %(id_cliente)s
                ORDER BY fecha_abono DESC;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultados is False:
            return []

        return [cls(fila) for fila in resultados]

    @staticmethod
    def validar(datos):
        es_valido = True

        try:
            monto = float(datos.get('monto', 0))

            if monto <= 0:
                flash(
                    'El abono debe ser mayor a cero.',
                    'error_saldo'
                )
                es_valido = False

        except (TypeError, ValueError):
            flash(
                'El monto del abono no es válido.',
                'error_saldo'
            )
            es_valido = False

        metodos_validos = [
            'efectivo',
            'transferencia'
        ]

        if datos.get('metodo_pago') not in metodos_validos:
            flash(
                'Selecciona un método de pago válido.',
                'error_metodo_pago'
            )
            es_valido = False

        return es_valido