from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_pacientes
from flask import flash
from app_flask import BASE_DATOS


class DatoClinico:
    def __init__(self, datos):
        self.id_dato_clinico = datos['id_dato_clinico']
        self.fecha = datos['fecha']
        self.retroalimentacion = datos['retroalimentacion']
        self.palpacion_examen = datos['palpacion_examen']
        self.trabajo_sesion = datos['trabajo_sesion']
        self.objetivos = datos['objetivos']
        self.trabajo_casa = datos['trabajo_casa']
        self.id_paciente = datos['id_paciente']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

        self.paciente = None

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO datos_clinicos(
                    fecha,
                    retroalimentacion,
                    palpacion_examen,
                    trabajo_sesion,
                    objetivos,
                    trabajo_casa,
                    id_paciente
                )
                VALUES(
                    %(fecha)s,
                    %(retroalimentacion)s,
                    %(palpacion_examen)s,
                    %(trabajo_sesion)s,
                    %(objetivos)s,
                    %(trabajo_casa)s,
                    %(id_paciente)s
                );
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM datos_clinicos
                WHERE id_dato_clinico = %(id_dato_clinico)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_paciente(cls, datos):
        query = """
                SELECT *
                FROM datos_clinicos
                WHERE id_paciente = %(id_paciente)s
                ORDER BY fecha DESC;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        datos_clinicos = []

        for fila in resultados:
            datos_clinicos.append(cls(fila))

        return datos_clinicos

    @classmethod
    def obtener_uno_con_paciente(cls, datos):
        query = """
                SELECT
                    datos_clinicos.*,

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
                    pacientes.fecha_actualizacion AS paciente_fecha_actualizacion,
                    pacientes.fecha_nacimiento AS paciente_fecha_nacimiento

                FROM datos_clinicos
                JOIN pacientes
                    ON datos_clinicos.id_paciente = pacientes.id_paciente
                WHERE datos_clinicos.id_dato_clinico = %(id_dato_clinico)s;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        fila = resultado[0]
        dato_clinico = cls(fila)

        datos_paciente = {
            "id_paciente": fila["paciente_id_paciente"],
            "nombre": fila["paciente_nombre"],
            "raza": fila["paciente_raza"],
            "edad": fila["paciente_edad"],
            "especie": fila["paciente_especie"],
            "sexo": fila["paciente_sexo"],
            "historia_clinica": fila["paciente_historia_clinica"],
            "inicio_problema": fila["paciente_inicio_problema"],
            "diagnostico_vet": fila["paciente_diagnostico_vet"],
            "id_cliente": fila["paciente_id_cliente"],
            "fecha_creacion": fila["paciente_fecha_creacion"],
            "fecha_actualizacion": fila["paciente_fecha_actualizacion"],
            "fecha_nacimiento": fila["paciente_fecha_nacimiento"],
        }

        dato_clinico.paciente = modelo_pacientes.Paciente(datos_paciente)

        return dato_clinico

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE datos_clinicos
                SET fecha = %(fecha)s,
                    retroalimentacion = %(retroalimentacion)s,
                    palpacion_examen = %(palpacion_examen)s,
                    trabajo_sesion = %(trabajo_sesion)s,
                    objetivos = %(objetivos)s,
                    trabajo_casa = %(trabajo_casa)s,
                    id_paciente = %(id_paciente)s
                WHERE id_dato_clinico = %(id_dato_clinico)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM datos_clinicos
                WHERE id_dato_clinico = %(id_dato_clinico)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @staticmethod
    def validar(datos):
        es_valido = True

        if not str(datos['id_paciente']).isdigit():
            flash('Debes seleccionar un paciente válido.', 'error_id_paciente')
            es_valido = False

        if len(datos['retroalimentacion'].strip()) < 5:
            flash('La retroalimentación debe tener al menos 5 caracteres.', 'error_retroalimentacion')
            es_valido = False

        if len(datos['palpacion_examen'].strip()) < 5:
            flash('La palpación/examen debe tener al menos 5 caracteres.', 'error_palpacion_examen')
            es_valido = False

        if len(datos['trabajo_sesion'].strip()) < 5:
            flash('El trabajo de sesión debe tener al menos 5 caracteres.', 'error_trabajo_sesion')
            es_valido = False

        if len(datos['objetivos'].strip()) < 5:
            flash('Las observaciones deben tener al menos 5 caracteres.', 'error_objetivos')
            es_valido = False

        if len(datos['trabajo_casa'].strip()) < 5:
            flash('El trabajo en casa debe tener al menos 5 caracteres.', 'error_trabajo_casa')
            es_valido = False

        return es_valido