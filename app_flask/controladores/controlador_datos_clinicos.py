from flask import render_template, redirect, request, session
from app_flask import app
from app_flask.modelos.modelo_datos_clinicos import DatoClinico
from app_flask.modelos.modelo_pacientes import Paciente


@app.route('/pacientes/<int:id_paciente>/datos-clinicos/nuevo', methods=['GET'])
def formulario_nuevo_dato_clinico(id_paciente):
    if 'id_administrador' not in session:
        return redirect('/')

    paciente = Paciente.obtener_por_id({
        'id_paciente': id_paciente
    })

    if paciente is None:
        return redirect('/pacientes')

    return render_template(
        'datos_clinicos/nuevo.html',
        paciente=paciente
    )


@app.route('/pacientes/<int:id_paciente>/datos-clinicos/crear', methods=['POST'])
def crear_dato_clinico(id_paciente):
    if 'id_administrador' not in session:
        return redirect('/')

    datos = {
        **request.form,
        'id_paciente': id_paciente
    }

    if not DatoClinico.validar(datos):
        return redirect(f'/pacientes/{id_paciente}/datos-clinicos/nuevo')

    DatoClinico.crear_uno(datos)

    return redirect(f'/pacientes/{id_paciente}')


@app.route('/datos-clinicos/<int:id_dato_clinico>', methods=['GET'])
def detalle_dato_clinico(id_dato_clinico):
    if 'id_administrador' not in session:
        return redirect('/')

    dato_clinico = DatoClinico.obtener_uno_con_paciente({
        'id_dato_clinico': id_dato_clinico
    })

    if dato_clinico is None:
        return redirect('/pacientes')

    return render_template(
        'datos_clinicos/detalle.html',
        dato_clinico=dato_clinico
    )


@app.route('/datos-clinicos/<int:id_dato_clinico>/editar', methods=['GET'])
def formulario_editar_dato_clinico(id_dato_clinico):
    if 'id_administrador' not in session:
        return redirect('/')

    dato_clinico = DatoClinico.obtener_por_id({
        'id_dato_clinico': id_dato_clinico
    })

    if dato_clinico is None:
        return redirect('/pacientes')

    return render_template(
        'datos_clinicos/editar.html',
        dato_clinico=dato_clinico
    )


@app.route('/datos-clinicos/<int:id_dato_clinico>/actualizar', methods=['POST'])
def actualizar_dato_clinico(id_dato_clinico):
    if 'id_administrador' not in session:
        return redirect('/')

    dato_clinico = DatoClinico.obtener_por_id({
        'id_dato_clinico': id_dato_clinico
    })

    if dato_clinico is None:
        return redirect('/pacientes')

    datos = {
        **request.form,
        'id_dato_clinico': id_dato_clinico,
        'id_paciente': dato_clinico.id_paciente
    }

    if not DatoClinico.validar(datos):
        return redirect(f'/datos-clinicos/{id_dato_clinico}/editar')

    DatoClinico.editar_uno(datos)

    return redirect(f'/pacientes/{dato_clinico.id_paciente}')


@app.route('/datos-clinicos/<int:id_dato_clinico>/eliminar', methods=['POST'])
def eliminar_dato_clinico(id_dato_clinico):
    if 'id_administrador' not in session:
        return redirect('/')

    dato_clinico = DatoClinico.obtener_por_id({
        'id_dato_clinico': id_dato_clinico
    })

    if dato_clinico is None:
        return redirect('/pacientes')

    id_paciente = dato_clinico.id_paciente

    DatoClinico.eliminar_uno({
        'id_dato_clinico': id_dato_clinico
    })

    return redirect(f'/pacientes/{id_paciente}')