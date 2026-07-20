from app_flask.controladores import controlador_admin, controlador_clientes, controlador_pacientes, controlador_productos, controlador_servicios, controlador_ordenes, controlador_datos_clinicos, controlador_caja
from app_flask import app

if __name__ == "__main__":
    app.run(debug = True )