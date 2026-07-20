from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_orden_servicios
from flask import flash
from app_flask import BASE_DATOS


class Servicio:
    def __init__(self, datos):
        self.id_servicio = datos['id_servicio']
        self.nombre = datos['nombre']
        self.descripcion = datos['descripcion']
        self.precio = datos['precio']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

        self.orden_servicios = []

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO servicios(
                    nombre,
                    descripcion,
                    precio
                )
                VALUES(
                    %(nombre)s,
                    %(descripcion)s,
                    %(precio)s
                );
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM servicios
                WHERE id_servicio = %(id_servicio)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_todos(cls):
        query = """
                SELECT *
                FROM servicios
                ORDER BY nombre;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        servicios = []

        for fila in resultados:
            servicios.append(cls(fila))

        return servicios

    @classmethod
    def obtener_con_ordenes(cls, datos):
        query = """
                SELECT *
                FROM servicios
                LEFT JOIN orden_servicios
                    ON servicios.id_servicio = orden_servicios.id_servicio
                WHERE servicios.id_servicio = %(id_servicio)s
                ORDER BY orden_servicios.fecha_creacion DESC;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        servicio = cls(resultado[0])

        for fila in resultado:
            if fila["orden_servicios.id_orden_servicio"] is not None:
                orden_servicio = {
                    "id_orden_servicio": fila["orden_servicios.id_orden_servicio"],
                    "id_orden": fila["id_orden"],
                    "id_servicio": fila["orden_servicios.id_servicio"],
                    "cantidad": fila["cantidad"],
                    "precio_unitario": fila["precio_unitario"],
                    "subtotal": fila["subtotal"],
                    "fecha_creacion": fila["orden_servicios.fecha_creacion"]
                }

                servicio.orden_servicios.append(
                    modelo_orden_servicios.OrdenServicio(orden_servicio)
                )

        return servicio

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE servicios
                SET nombre = %(nombre)s,
                    descripcion = %(descripcion)s,
                    precio = %(precio)s
                WHERE id_servicio = %(id_servicio)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM servicios
                WHERE id_servicio = %(id_servicio)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def buscar(cls, datos):
        query = """
                SELECT *
                FROM servicios
                WHERE nombre LIKE %(busqueda)s
                OR descripcion LIKE %(busqueda)s
                ORDER BY nombre;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultados == False:
            return []

        servicios = []

        for fila in resultados:
            servicios.append(cls(fila))

        return servicios

    @staticmethod
    def validar(datos):
        es_valido = True

        if len(datos['nombre'].strip()) < 2:
            flash('El nombre del servicio debe tener al menos 2 caracteres.', 'error_nombre')
            es_valido = False

        if len(datos['descripcion'].strip()) < 5:
            flash('La descripción debe tener al menos 5 caracteres.', 'error_descripcion')
            es_valido = False

        try:
            precio = float(datos['precio'])

            if precio < 0:
                flash('El precio no puede ser negativo.', 'error_precio')
                es_valido = False

        except:
            flash('El precio debe ser un número válido.', 'error_precio')
            es_valido = False

        return es_valido