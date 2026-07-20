from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_orden_productos
from flask import flash
from app_flask import BASE_DATOS


class Producto:
    def __init__(self, datos):
        self.id_producto = datos['id_producto']
        self.nombre = datos['nombre']
        self.precio = datos['precio']
        self.stock = datos['stock']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

        self.orden_productos = []

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO productos(
                    nombre,
                    precio,
                    stock
                )
                VALUES(
                    %(nombre)s,
                    %(precio)s,
                    %(stock)s
                );
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM productos
                WHERE id_producto = %(id_producto)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_todos(cls):
        query = """
                SELECT *
                FROM productos
                ORDER BY nombre;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        productos = []

        for fila in resultados:
            productos.append(cls(fila))

        return productos

    @classmethod
    def obtener_con_ordenes(cls, datos):
        query = """
                SELECT *
                FROM productos
                LEFT JOIN orden_productos
                    ON productos.id_producto = orden_productos.id_producto
                WHERE productos.id_producto = %(id_producto)s
                ORDER BY orden_productos.fecha_creacion DESC;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        producto = cls(resultado[0])

        for fila in resultado:
            if fila["orden_productos.id_orden_producto"] is not None:
                orden_producto = {
                    "id_orden_producto": fila["orden_productos.id_orden_producto"],
                    "id_orden": fila["id_orden"],
                    "id_producto": fila["orden_productos.id_producto"],
                    "cantidad": fila["cantidad"],
                    "precio_unitario": fila["precio_unitario"],
                    "subtotal": fila["subtotal"],
                    "fecha_creacion": fila["orden_productos.fecha_creacion"]
                }

                producto.orden_productos.append(
                    modelo_orden_productos.OrdenProducto(orden_producto)
                )

        return producto

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE productos
                SET nombre = %(nombre)s,
                    precio = %(precio)s,
                    stock = %(stock)s
                WHERE id_producto = %(id_producto)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM productos
                WHERE id_producto = %(id_producto)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def actualizar_stock(cls, datos):
        query = """
                UPDATE productos
                SET stock = %(stock)s
                WHERE id_producto = %(id_producto)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def disminuir_stock(cls, datos):
        query = """
                UPDATE productos
                SET stock = stock - %(cantidad)s
                WHERE id_producto = %(id_producto)s
                    AND stock >= %(cantidad)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def aumentar_stock(cls, datos):
        query = """
                UPDATE productos
                SET stock = stock + %(cantidad)s
                WHERE id_producto = %(id_producto)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_con_stock_bajo(cls, datos):
        query = """
                SELECT *
                FROM productos
                WHERE stock <= %(stock_minimo)s
                ORDER BY stock ASC;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        productos = []

        for fila in resultados:
            productos.append(cls(fila))

        return productos
    
    @classmethod
    def buscar(cls, datos):
        query = """
                SELECT *
                FROM productos
                WHERE nombre LIKE %(busqueda)s
                ORDER BY nombre;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultados == False:
            return []

        productos = []

        for fila in resultados:
            productos.append(cls(fila))

        return productos

    @staticmethod
    def validar(datos):
        es_valido = True

        if len(datos['nombre'].strip()) < 2:
            flash('El nombre del producto debe tener al menos 2 caracteres.', 'error_nombre')
            es_valido = False

        try:
            precio = float(datos['precio'])

            if precio < 0:
                flash('El precio no puede ser negativo.', 'error_precio')
                es_valido = False

        except:
            flash('El precio debe ser un número válido.', 'error_precio')
            es_valido = False

        try:
            stock = int(datos['stock'])

            if stock < 0:
                flash('El stock no puede ser negativo.', 'error_stock')
                es_valido = False

        except:
            flash('El stock debe ser un número entero.', 'error_stock')
            es_valido = False

        return es_valido