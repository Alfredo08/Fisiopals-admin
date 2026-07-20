from app_flask.config.mysqlconnection import connectToMySQL
from flask import flash
from app_flask import BASE_DATOS, EMAIL_REGEX


class Administrador:
    def __init__(self, datos):
        self.id_administrador = datos['id_administrador']
        self.nombre_completo = datos['nombre_completo']
        self.correo = datos['correo']
        self.password = datos['password']

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO administradores(
                    nombre_completo,
                    correo,
                    password
                )
                VALUES(
                    %(nombre_completo)s,
                    %(correo)s,
                    %(password)s
                );
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM administradores
                WHERE id_administrador = %(id_administrador)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_correo(cls, datos):
        query = """
                SELECT *
                FROM administradores
                WHERE correo = %(correo)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_todos(cls):
        query = """
                SELECT *
                FROM administradores
                ORDER BY nombre_completo;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        administradores = []

        for fila in resultados:
            administradores.append(cls(fila))

        return administradores

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE administradores
                SET nombre_completo = %(nombre_completo)s,
                    correo = %(correo)s
                WHERE id_administrador = %(id_administrador)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def actualizar_password(cls, datos):
        query = """
                UPDATE administradores
                SET password = %(password)s
                WHERE id_administrador = %(id_administrador)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM administradores
                WHERE id_administrador = %(id_administrador)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @staticmethod
    def validar(datos):
        es_valido = True

        if len(datos['nombre_completo'].strip()) < 3:
            flash(
                'El nombre debe tener al menos 3 caracteres.',
                'error_nombre_completo'
            )
            es_valido = False

        if not EMAIL_REGEX.match(datos['correo']):
            flash(
                'Por favor ingresa un correo válido.',
                'error_correo'
            )
            es_valido = False

        if len(datos['password']) < 8:
            flash(
                'La contraseña debe tener al menos 8 caracteres.',
                'error_password'
            )
            es_valido = False

        if 'password_confirmar' in datos:
            if datos['password'] != datos['password_confirmar']:
                flash(
                    'Las contraseñas no coinciden.',
                    'error_password'
                )
                es_valido = False

        return es_valido