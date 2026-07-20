from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_pacientes
from flask import flash
from app_flask import BASE_DATOS, EMAIL_REGEX

class Cliente:
    def __init__(self, datos):
        self.id_cliente = datos['id_cliente']
        self.nombre = datos['nombre']
        self.correo = datos['correo']
        self.telefono = datos['telefono']
        self.saldo = datos['saldo']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

        self.pacientes = []

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO clientes(
                    nombre,
                    correo,
                    telefono
                )
                VALUES(
                    %(nombre)s,
                    %(correo)s,
                    %(telefono)s
                );
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM clientes
                WHERE id_cliente = %(id_cliente)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_correo(cls, datos):
        query = """
                SELECT *
                FROM clientes
                WHERE correo = %(correo)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_telefono(cls, datos):
        query = """
                SELECT *
                FROM clientes
                WHERE telefono = %(telefono)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_todos(cls):
        query = """
                SELECT *
                FROM clientes
                ORDER BY nombre;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        clientes = []

        for fila in resultados:
            clientes.append(cls(fila))

        return clientes

    @classmethod
    def obtener_con_pacientes(cls, datos):
        query = """
                SELECT
                    clientes.*,

                    pacientes.id_paciente AS paciente_id_paciente,
                    pacientes.nombre AS paciente_nombre,
                    pacientes.raza AS paciente_raza,
                    pacientes.edad AS paciente_edad,
                    pacientes.especie AS paciente_especie,
                    pacientes.sexo AS paciente_sexo,
                    pacientes.historia_clinica AS paciente_historia_clinica,
                    pacientes.inicio_problema AS paciente_inicio_problema,
                    pacientes.diagnostico_vet AS paciente_diagnostico_vet,
                    pacientes.id_cliente AS paciente_id_cliente,
                    pacientes.fecha_creacion AS paciente_fecha_creacion,
                    pacientes.fecha_actualizacion AS paciente_fecha_actualizacion

                FROM clientes
                LEFT JOIN pacientes
                    ON clientes.id_cliente = pacientes.id_cliente
                WHERE clientes.id_cliente = %(id_cliente)s;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        cliente = cls(resultado[0])

        for fila in resultado:
            if fila['paciente_id_paciente'] is not None:
                datos_paciente = {
                    "id_paciente": fila['paciente_id_paciente'],
                    "nombre": fila['paciente_nombre'],
                    "raza": fila['paciente_raza'],
                    "edad": fila['paciente_edad'],
                    "especie": fila['paciente_especie'],
                    "sexo": fila['paciente_sexo'],
                    "historia_clinica": fila['paciente_historia_clinica'],
                    "inicio_problema": fila['paciente_inicio_problema'],
                    "diagnostico_vet": fila['paciente_diagnostico_vet'],
                    "id_cliente": fila['paciente_id_cliente'],
                    "fecha_creacion": fila['paciente_fecha_creacion'],
                    "fecha_actualizacion": fila['paciente_fecha_actualizacion']
                }

                cliente.pacientes.append(
                    modelo_pacientes.Paciente(datos_paciente)
                )

        return cliente

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE clientes
                SET nombre = %(nombre)s,
                    correo = %(correo)s,
                    telefono = %(telefono)s,
                    saldo = %(saldo)s
                WHERE id_cliente = %(id_cliente)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM clientes
                WHERE id_cliente = %(id_cliente)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def buscar(cls, datos):
        query = """
                SELECT *
                FROM clientes
                WHERE nombre LIKE %(busqueda)s
                OR correo LIKE %(busqueda)s
                OR telefono LIKE %(busqueda)s
                ORDER BY nombre;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultados == False:
            return []

        clientes = []

        for fila in resultados:
            clientes.append(cls(fila))

        return clientes
        
    @classmethod
    def descontar_saldo(cls, datos):
        query = """
                UPDATE clientes
                SET saldo = saldo - %(monto)s
                WHERE id_cliente = %(id_cliente)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def agregar_saldo(cls, datos):
        query = """
                UPDATE clientes
                SET saldo = saldo + %(monto)s
                WHERE id_cliente = %(id_cliente)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def abonar_saldo(cls, datos):
        query = """
                UPDATE clientes
                SET saldo = saldo + %(monto)s
                WHERE id_cliente = %(id_cliente)s;
                """

        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @staticmethod
    def validar(datos):
        es_valido = True

        if len(datos['nombre'].strip()) < 2:
            flash('El nombre debe tener al menos 2 caracteres.', 'error_nombre')
            es_valido = False

        if not EMAIL_REGEX.match(datos['correo']):
            flash('Por favor ingresa un correo válido.', 'error_correo')
            es_valido = False

        if len(datos['telefono'].strip()) < 8:
            flash('Por favor ingresa un teléfono válido.', 'error_telefono')
            es_valido = False

        return es_valido