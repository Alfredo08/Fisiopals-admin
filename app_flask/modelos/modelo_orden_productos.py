from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_productos
from flask import flash
from app_flask import BASE_DATOS


class OrdenProducto:
    def __init__(self, datos):
        self.id_orden_producto = datos['id_orden_producto']
        self.id_orden = datos['id_orden']
        self.id_producto = datos['id_producto']
        self.cantidad = datos['cantidad']
        self.precio_unitario = datos['precio_unitario']
        self.subtotal = datos['subtotal']
        self.fecha_creacion = datos['fecha_creacion']

        self.producto = None

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO orden_productos(
                    id_orden,
                    id_producto,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES(
                    %(id_orden)s,
                    %(id_producto)s,
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
                FROM orden_productos
                WHERE id_orden_producto = %(id_orden_producto)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_orden(cls, datos):
        query = """
                SELECT *
                FROM orden_productos
                WHERE id_orden = %(id_orden)s;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        productos = []

        for fila in resultados:
            productos.append(cls(fila))

        return productos

    @classmethod
    def obtener_por_orden_con_producto(cls, datos):
        query = """
                SELECT
                    orden_productos.*,

                    productos.id_producto AS producto_id_producto,
                    productos.nombre AS producto_nombre,
                    productos.precio AS producto_precio,
                    productos.stock AS producto_stock,
                    productos.fecha_creacion AS producto_fecha_creacion,
                    productos.fecha_actualizacion AS producto_fecha_actualizacion

                FROM orden_productos
                JOIN productos
                    ON orden_productos.id_producto = productos.id_producto
                WHERE orden_productos.id_orden = %(id_orden)s;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        orden_productos = []

        for fila in resultados:
            orden_producto = cls(fila)

            producto = {
                "id_producto": fila["producto_id_producto"],
                "nombre": fila["producto_nombre"],
                "precio": fila["producto_precio"],
                "stock": fila["producto_stock"],
                "fecha_creacion": fila["producto_fecha_creacion"],
                "fecha_actualizacion": fila["producto_fecha_actualizacion"]
            }

            orden_producto.producto = modelo_productos.Producto(producto)
            orden_productos.append(orden_producto)

        return orden_productos

    @classmethod
    def obtener_uno_con_producto(cls, datos):
        query = """
                SELECT *
                FROM orden_productos
                JOIN productos
                    ON orden_productos.id_producto = productos.id_producto
                WHERE orden_productos.id_orden_producto = %(id_orden_producto)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        fila = resultado[0]
        orden_producto = cls(fila)

        producto = {
            "id_producto": fila["productos.id_producto"],
            "nombre": fila["nombre"],
            "precio": fila["precio"],
            "stock": fila["stock"],
            "fecha_creacion": fila["productos.fecha_creacion"],
            "fecha_actualizacion": fila["productos.fecha_actualizacion"]
        }

        orden_producto.producto = modelo_productos.Producto(producto)

        return orden_producto

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE orden_productos
                SET id_producto = %(id_producto)s,
                    cantidad = %(cantidad)s,
                    precio_unitario = %(precio_unitario)s,
                    subtotal = %(subtotal)s
                WHERE id_orden_producto = %(id_orden_producto)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM orden_productos
                WHERE id_orden_producto = %(id_orden_producto)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @staticmethod
    def validar(datos):
        es_valido = True

        if not str(datos['id_orden']).isdigit():
            flash('La orden no es válida.', 'error_id_orden')
            es_valido = False

        if not str(datos['id_producto']).isdigit():
            flash('El producto no es válido.', 'error_id_producto')
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