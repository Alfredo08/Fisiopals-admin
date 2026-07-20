from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_servicios
from flask import flash
from app_flask import BASE_DATOS


class OrdenServicio:
    def __init__(self, datos):
        self.id_orden_servicio = datos['id_orden_servicio']
        self.id_orden = datos['id_orden']
        self.id_servicio = datos['id_servicio']
        self.cantidad = datos['cantidad']
        self.precio_unitario = datos['precio_unitario']
        self.subtotal = datos['subtotal']
        self.fecha_creacion = datos['fecha_creacion']

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO orden_servicios(
                    id_orden,
                    id_servicio,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES(
                    %(id_orden)s,
                    %(id_servicio)s,
                    %(cantidad)s,
                    %(precio_unitario)s,
                    %(subtotal)s
                );
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM orden_servicios
                WHERE id_orden_servicio = %(id_orden_servicio)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_orden(cls, datos):
        query = """
                SELECT *
                FROM orden_servicios
                WHERE id_orden = %(id_orden)s;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        servicios = []

        for fila in resultados:
            servicios.append(cls(fila))

        return servicios

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE orden_servicios
                SET id_servicio = %(id_servicio)s,
                    cantidad = %(cantidad)s,
                    precio_unitario = %(precio_unitario)s,
                    subtotal = %(subtotal)s
                WHERE id_orden_servicio = %(id_orden_servicio)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM orden_servicios
                WHERE id_orden_servicio = %(id_orden_servicio)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_orden_con_servicio(cls, datos):
        query = """
                SELECT
                    orden_servicios.*,

                    servicios.id_servicio AS servicio_id_servicio,
                    servicios.nombre AS servicio_nombre,
                    servicios.descripcion AS servicio_descripcion,
                    servicios.precio AS servicio_precio,
                    servicios.fecha_creacion AS servicio_fecha_creacion,
                    servicios.fecha_actualizacion AS servicio_fecha_actualizacion

                FROM orden_servicios
                JOIN servicios
                    ON orden_servicios.id_servicio = servicios.id_servicio
                WHERE orden_servicios.id_orden = %(id_orden)s;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        orden_servicios = []

        for fila in resultados:
            orden_servicio = cls(fila)

            servicio = {
                "id_servicio": fila["servicio_id_servicio"],
                "nombre": fila["servicio_nombre"],
                "descripcion": fila["servicio_descripcion"],
                "precio": fila["servicio_precio"],
                "fecha_creacion": fila["servicio_fecha_creacion"],
                "fecha_actualizacion": fila["servicio_fecha_actualizacion"]
            }

            orden_servicio.servicio = modelo_servicios.Servicio(servicio)
            orden_servicios.append(orden_servicio)

        return orden_servicios

    @staticmethod
    def validar(datos):
        es_valido = True

        if not str(datos['id_orden']).isdigit():
            flash('La orden no es válida.', 'error_id_orden')
            es_valido = False

        if not str(datos['id_servicio']).isdigit():
            flash('El servicio no es válido.', 'error_id_servicio')
            es_valido = False

        try:
            cantidad = int(datos['cantidad'])

            if cantidad <= 0:
                flash('La cantidad debe ser mayor a 0.', 'error_cantidad')
                es_valido = False

        except:
            flash('La cantidad debe ser un número entero.', 'error_cantidad')
            es_valido = False

        try:
            precio_unitario = float(datos['precio_unitario'])

            if precio_unitario < 0:
                flash('El precio unitario no puede ser negativo.', 'error_precio_unitario')
                es_valido = False

        except:
            flash('El precio unitario debe ser un número válido.', 'error_precio_unitario')
            es_valido = False

        try:
            subtotal = float(datos['subtotal'])

            if subtotal < 0:
                flash('El subtotal no puede ser negativo.', 'error_subtotal')
                es_valido = False

        except:
            flash('El subtotal debe ser un número válido.', 'error_subtotal')
            es_valido = False

        return es_valido