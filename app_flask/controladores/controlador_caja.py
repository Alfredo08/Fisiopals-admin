from datetime import date

from flask import render_template, redirect, request, session

from app_flask import app
from app_flask.modelos.modelo_caja import MovimientoCaja
from app_flask.modelos.modelo_caja import AplicacionSaldo


@app.route('/caja', methods=['GET'])
def mostrar_caja():
    if 'id_administrador' not in session:
        return redirect('/')

    fecha_seleccionada = request.args.get(
        'fecha',
        ''
    ).strip()

    if fecha_seleccionada == '':
        fecha_seleccionada = date.today().isoformat()

    datos = {
        'fecha': fecha_seleccionada
    }

    movimientos = MovimientoCaja.obtener_por_fecha(datos)

    totales = MovimientoCaja.obtener_totales_por_fecha(datos)

    aplicaciones_saldo = AplicacionSaldo.obtener_por_fecha(
        datos
    )

    return render_template(
        'caja/index.html',
        movimientos=movimientos,
        totales=totales,
        aplicaciones_saldo=aplicaciones_saldo,
        fecha_seleccionada=fecha_seleccionada
    )