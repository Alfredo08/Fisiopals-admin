from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.modelos import modelo_clientes
from app_flask.modelos import modelo_datos_clinicos
from app_flask.modelos import modelo_ordenes
from flask import flash
from app_flask import BASE_DATOS


class Paciente:
    def __init__(self, datos):
        self.id_paciente = datos['id_paciente']
        self.nombre = datos['nombre']
        self.raza = datos['raza']
        self.edad = datos['edad']
        self.especie = datos['especie']
        self.sexo = datos['sexo']
        self.historia_clinica = datos['historia_clinica']
        self.inicio_problema = datos['inicio_problema']
        self.diagnostico_vet = datos['diagnostico_vet']
        self.id_cliente = datos['id_cliente']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']
        self.fecha_nacimiento = datos['fecha_nacimiento']

        self.cliente = None
        self.datos_clinicos = []
        self.ordenes = []

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO pacientes(
                    nombre,
                    raza,
                    fecha_nacimiento,
                    edad,
                    especie,
                    sexo,
                    historia_clinica,
                    inicio_problema,
                    diagnostico_vet,
                    id_cliente
                )
                VALUES(
                    %(nombre)s,
                    %(raza)s,
                    %(fecha_nacimiento)s,
                    %(edad)s,
                    %(especie)s,
                    %(sexo)s,
                    %(historia_clinica)s,
                    %(inicio_problema)s,
                    %(diagnostico_vet)s,
                    %(id_cliente)s
                );
                """

        return connectToMySQL(BASE_DATOS).query_db(
            query,
            datos
        )

    @classmethod
    def obtener_por_id(cls, datos):
        query = """
                SELECT *
                FROM pacientes
                WHERE id_paciente = %(id_paciente)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_todos(cls):
        query = """
                SELECT *
                FROM pacientes
                ORDER BY nombre;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        pacientes = []

        for fila in resultados:
            pacientes.append(cls(fila))

        return pacientes

    @classmethod
    def obtener_por_cliente(cls, datos):
        query = """
                SELECT *
                FROM pacientes
                WHERE id_cliente = %(id_cliente)s
                ORDER BY nombre;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        pacientes = []

        for fila in resultados:
            pacientes.append(cls(fila))

        return pacientes

    @classmethod
    def obtener_uno_con_cliente(cls, datos):
        query = """
                SELECT *
                FROM pacientes
                JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente
                WHERE pacientes.id_paciente = %(id_paciente)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        fila = resultado[0]
        paciente = cls(fila)

        datos_cliente = {
            "id_cliente": fila["clientes.id_cliente"],
            "nombre": fila["clientes.nombre"],
            "correo": fila["correo"],
            "telefono": fila["telefono"],
            "saldo": fila["saldo"],
            "fecha_creacion": fila["clientes.fecha_creacion"],
            "fecha_actualizacion": fila["clientes.fecha_actualizacion"]
        }

        paciente.cliente = modelo_clientes.Cliente(datos_cliente)

        return paciente

    @classmethod
    def obtener_uno_con_datos_clinicos(cls, datos):
        query = """
                SELECT
                    pacientes.*,

                    datos_clinicos.id_dato_clinico AS dato_id_dato_clinico,
                    datos_clinicos.fecha AS dato_fecha,
                    datos_clinicos.retroalimentacion AS dato_retroalimentacion,
                    datos_clinicos.palpacion_examen AS dato_palpacion_examen,
                    datos_clinicos.trabajo_sesion AS dato_trabajo_sesion,
                    datos_clinicos.objetivos AS dato_objetivos,
                    datos_clinicos.trabajo_casa AS dato_trabajo_casa,
                    datos_clinicos.id_paciente AS dato_id_paciente,
                    datos_clinicos.fecha_creacion AS dato_fecha_creacion,
                    datos_clinicos.fecha_actualizacion AS dato_fecha_actualizacion

                FROM pacientes
                LEFT JOIN datos_clinicos
                    ON pacientes.id_paciente = datos_clinicos.id_paciente
                WHERE pacientes.id_paciente = %(id_paciente)s
                ORDER BY datos_clinicos.fecha DESC;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        paciente = cls(resultado[0])

        for fila in resultado:
            if fila["dato_id_dato_clinico"] is not None:
                dato_clinico = {
                    "id_dato_clinico": fila["dato_id_dato_clinico"],
                    "fecha": fila["dato_fecha"],
                    "retroalimentacion": fila["dato_retroalimentacion"],
                    "palpacion_examen": fila["dato_palpacion_examen"],
                    "trabajo_sesion": fila["dato_trabajo_sesion"],
                    "objetivos": fila["dato_objetivos"],
                    "trabajo_casa": fila["dato_trabajo_casa"],
                    "id_paciente": fila["dato_id_paciente"],
                    "fecha_creacion": fila["dato_fecha_creacion"],
                    "fecha_actualizacion": fila["dato_fecha_actualizacion"]
                }

                paciente.datos_clinicos.append(
                    modelo_datos_clinicos.DatoClinico(dato_clinico)
                )

        return paciente

    @classmethod
    def obtener_uno_con_ordenes(cls, datos):
        query = """
                SELECT *
                FROM pacientes
                LEFT JOIN ordenes
                    ON pacientes.id_paciente = ordenes.id_paciente
                WHERE pacientes.id_paciente = %(id_paciente)s
                ORDER BY ordenes.fecha_creacion DESC;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        paciente = cls(resultado[0])

        for fila in resultado:
            if fila["ordenes.id_orden"] is not None:
                orden = {
                    "id_orden": fila["ordenes.id_orden"],
                    "id_paciente": fila["ordenes.id_paciente"],
                    "nombre_comprador": fila["nombre_comprador"],
                    "estado": fila["estado"],
                    "total": fila["total"],
                    "fecha_creacion": fila["ordenes.fecha_creacion"],
                    "fecha_actualizacion": fila["ordenes.fecha_actualizacion"]
                }

                paciente.ordenes.append(
                    modelo_ordenes.Orden(orden)
                )

        return paciente

    @classmethod
    def editar_uno(cls, datos):
        query = """
                UPDATE pacientes
                SET nombre = %(nombre)s,
                    raza = %(raza)s,
                    fecha_nacimiento = %(fecha_nacimiento)s,
                    edad = %(edad)s,
                    especie = %(especie)s,
                    sexo = %(sexo)s,
                    historia_clinica = %(historia_clinica)s,
                    inicio_problema = %(inicio_problema)s,
                    diagnostico_vet = %(diagnostico_vet)s,
                    id_cliente = %(id_cliente)s
                WHERE id_paciente = %(id_paciente)s;
                """

        return connectToMySQL(BASE_DATOS).query_db(
            query,
            datos
        )

    @classmethod
    def eliminar_uno(cls, datos):
        query = """
                DELETE FROM pacientes
                WHERE id_paciente = %(id_paciente)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def buscar(cls, datos):
        query = """
                SELECT *
                FROM pacientes
                WHERE nombre LIKE %(busqueda)s
                OR raza LIKE %(busqueda)s
                OR especie LIKE %(busqueda)s
                OR sexo LIKE %(busqueda)s
                ORDER BY nombre;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if resultados == False:
            return []

        pacientes = []

        for fila in resultados:
            pacientes.append(cls(fila))

        return pacientes
    
    @classmethod
    def obtener_todos_con_cliente(cls):
        query = """
                SELECT
                    pacientes.*,

                    clientes.id_cliente AS cliente_id_cliente,
                    clientes.nombre AS cliente_nombre,
                    clientes.correo AS cliente_correo,
                    clientes.telefono AS cliente_telefono,
                    clientes.saldo AS cliente_saldo,
                    clientes.fecha_creacion AS cliente_fecha_creacion,
                    clientes.fecha_actualizacion AS cliente_fecha_actualizacion

                FROM pacientes
                JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente

                ORDER BY pacientes.nombre;
                """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        pacientes = []

        for fila in resultados:
            paciente = cls(fila)

            datos_cliente = {
                "id_cliente": fila["cliente_id_cliente"],
                "nombre": fila["cliente_nombre"],
                "correo": fila["cliente_correo"],
                "telefono": fila["cliente_telefono"],
                "saldo": fila["cliente_saldo"],
                "fecha_creacion": fila["cliente_fecha_creacion"],
                "fecha_actualizacion": fila["cliente_fecha_actualizacion"]
            }

            paciente.cliente = modelo_clientes.Cliente(datos_cliente)

            pacientes.append(paciente)

        return pacientes
    
    @classmethod
    def obtener_uno_completo(cls, datos):
        query = """
                SELECT
                    pacientes.*,

                    clientes.id_cliente AS cliente_id_cliente,
                    clientes.nombre AS cliente_nombre,
                    clientes.correo AS cliente_correo,
                    clientes.telefono AS cliente_telefono,
                    clientes.saldo AS cliente_saldo,
                    clientes.fecha_creacion AS cliente_fecha_creacion,
                    clientes.fecha_actualizacion AS cliente_fecha_actualizacion,

                    datos_clinicos.id_dato_clinico AS dato_id_dato_clinico,
                    datos_clinicos.fecha AS dato_fecha,
                    datos_clinicos.retroalimentacion AS dato_retroalimentacion,
                    datos_clinicos.palpacion_examen AS dato_palpacion_examen,
                    datos_clinicos.trabajo_sesion AS dato_trabajo_sesion,
                    datos_clinicos.objetivos AS dato_objetivos,
                    datos_clinicos.trabajo_casa AS dato_trabajo_casa,
                    datos_clinicos.id_paciente AS dato_id_paciente,
                    datos_clinicos.fecha_creacion AS dato_fecha_creacion,
                    datos_clinicos.fecha_actualizacion AS dato_fecha_actualizacion

                FROM pacientes
                JOIN clientes
                    ON pacientes.id_cliente = clientes.id_cliente
                LEFT JOIN datos_clinicos
                    ON pacientes.id_paciente = datos_clinicos.id_paciente
                WHERE pacientes.id_paciente = %(id_paciente)s
                ORDER BY datos_clinicos.fecha DESC;
                """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)

        if len(resultado) < 1:
            return None

        paciente = cls(resultado[0])

        datos_cliente = {
            "id_cliente": resultado[0]["cliente_id_cliente"],
            "nombre": resultado[0]["cliente_nombre"],
            "correo": resultado[0]["cliente_correo"],
            "telefono": resultado[0]["cliente_telefono"],
            "saldo": resultado[0]["cliente_saldo"],
            "fecha_creacion": resultado[0]["cliente_fecha_creacion"],
            "fecha_actualizacion": resultado[0]["cliente_fecha_actualizacion"]
        }

        paciente.cliente = modelo_clientes.Cliente(datos_cliente)

        for fila in resultado:
            if fila["dato_id_dato_clinico"] is not None:
                dato_clinico = {
                    "id_dato_clinico": fila["dato_id_dato_clinico"],
                    "fecha": fila["dato_fecha"],
                    "retroalimentacion": fila["dato_retroalimentacion"],
                    "palpacion_examen": fila["dato_palpacion_examen"],
                    "trabajo_sesion": fila["dato_trabajo_sesion"],
                    "objetivos": fila["dato_objetivos"],
                    "trabajo_casa": fila["dato_trabajo_casa"],
                    "id_paciente": fila["dato_id_paciente"],
                    "fecha_creacion": fila["dato_fecha_creacion"],
                    "fecha_actualizacion": fila["dato_fecha_actualizacion"]
                }

                paciente.datos_clinicos.append(
                    modelo_datos_clinicos.DatoClinico(dato_clinico)
                )

        return paciente    
    
    @staticmethod
    def validar(datos):
        es_valido = True

        if len(datos.get('nombre', '').strip()) < 2:
            flash(
                'El nombre del paciente debe tener al menos 2 caracteres.',
                'error_nombre'
            )
            es_valido = False

        if len(datos.get('raza', '').strip()) < 2:
            flash(
                'La raza debe tener al menos 2 caracteres.',
                'error_raza'
            )
            es_valido = False

        edad = str(datos.get('edad', '')).strip()


        especies_validas = [
            'Canino',
            'Felino',
            'Equino',
            'No convencional'
        ]

        if datos.get('especie') not in especies_validas:
            flash(
                'La especie seleccionada no es válida.',
                'error_especie'
            )
            es_valido = False

        sexos_validos = [
            'Macho',
            'Macho castrado',
            'Hembra',
            'Hembra castrada'
        ]

        if datos.get('sexo') not in sexos_validos:
            flash(
                'El sexo seleccionado no es válido.',
                'error_sexo'
            )
            es_valido = False

        # Historia clínica opcional.
        historia_clinica = datos.get(
            'historia_clinica',
            ''
        ).strip()

        if historia_clinica and len(historia_clinica) < 5:
            flash(
                (
                    'Si capturas la historia clínica, '
                    'debe tener al menos 5 caracteres.'
                ),
                'error_historia_clinica'
            )
            es_valido = False

        # Diagnóstico veterinario opcional.
        diagnostico_vet = datos.get(
            'diagnostico_vet',
            ''
        ).strip()

        if diagnostico_vet and len(diagnostico_vet) < 5:
            flash(
                (
                    'Si capturas el diagnóstico veterinario, '
                    'debe tener al menos 5 caracteres.'
                ),
                'error_diagnostico_vet'
            )
            es_valido = False

        if not str(datos.get('id_cliente', '')).isdigit():
            flash(
                'Debes seleccionar un cliente válido.',
                'error_id_cliente'
            )
            es_valido = False

        return es_valido

    def codigo_paciente(self):
        return f"000-{self.id_paciente:03d}"