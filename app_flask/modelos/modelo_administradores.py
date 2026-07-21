from app_flask.config.mysqlconnection import connectToMySQL
from flask import flash
from app_flask import BASE_DATOS, USUARIO_REGEX


class Administrador:
    def __init__(self, datos):
        self.id_administrador = datos['id_administrador']
        self.nombre_completo = datos['nombre_completo']
        self.nombre_usuario = datos['nombre_usuario']
        self.password = datos['password']
        self.puede_gestionar_catalogo = bool(
            datos.get('puede_gestionar_catalogo', 0)
        )

    @classmethod
    def crear_uno(cls, datos):
        query = """
                    INSERT INTO administradores(
                        nombre_completo,
                        nombre_usuario,
                        password,
                        puede_gestionar_catalogo
                    )
                    VALUES(
                        %(nombre_completo)s,
                        %(nombre_usuario)s,
                        %(password)s,
                        0
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
    def obtener_por_nombre_usuario(cls, datos):
        query = """
                SELECT *
                FROM administradores
                WHERE nombre_usuario = %(nombre_usuario)s;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultado is False or len(resultado) < 1:
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

        nombre_completo = datos.get(
            'nombre_completo',
            ''
        ).strip()

        nombre_usuario = datos.get(
            'nombre_usuario',
            ''
        ).strip()

        password = datos.get(
            'password',
            ''
        )

        password_confirmar = datos.get(
            'password_confirmar',
            ''
        )

        if len(nombre_completo) < 3:
            flash(
                'El nombre debe tener al menos 3 caracteres.',
                'error_nombre_completo'
            )
            es_valido = False

        if len(nombre_usuario) < 4:
            flash(
                'El nombre de usuario debe tener al menos 4 caracteres.',
                'error_nombre_usuario'
            )
            es_valido = False

        elif not USUARIO_REGEX.match(nombre_usuario):
            flash(
                (
                    'El nombre de usuario solo puede contener '
                    'letras, números, puntos, guiones y guiones bajos.'
                ),
                'error_nombre_usuario'
            )
            es_valido = False

        if len(password) < 8:
            flash(
                'La contraseña debe tener al menos 8 caracteres.',
                'error_password'
            )
            es_valido = False

        if 'password_confirmar' in datos:
            if password != password_confirmar:
                flash(
                    'Las contraseñas no coinciden.',
                    'error_password'
                )
                es_valido = False

        return es_valido