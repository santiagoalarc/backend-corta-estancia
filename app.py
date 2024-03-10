from flask import Flask, app
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from vistas.bancos import VistaBancos
from vistas.movimiento import VistaMovimiento
from vistas.movimientos import VistaMovimientos
from vistas.propiedades import VistaPropiedades
from vistas.propiedad import VistaPropiedad
from vistas.reserva import VistaReserva
from vistas.reservas import VistaReservas
from vistas.sign_in import VistaSignIn
from vistas.login import VistaLogIn
from vistas.usuario import VistaUsuario
from modelos import db, Usuario
from vistas.tipo_movimientos import VistaTipoMovimientos
from vistas.sign_in_propietarios import VistaSignInPropietarios
from vistas.tipo_identificacion import VistaTipoIdentificacion
from vistas.tipo_usuario import VistaTipoUsuario


def create_flask_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admon_reservas.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app_context = app.app_context()
    app_context.push()
    add_urls(app)

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return Usuario.query.filter_by(id=identity).one_or_none()

    return app


def add_urls(app):
    api = Api(app)
    api.add_resource(VistaSignIn, "/signin", "/signin/<int:id_usuario>", "/usuarios")
    api.add_resource(VistaSignInPropietarios, "/signin/propietarios/<int:id_usuario>", "/propietarios")
    api.add_resource(VistaLogIn, "/login")
    api.add_resource(VistaUsuario, '/usuarios')
    api.add_resource(VistaPropiedades, "/propiedades")
    api.add_resource(VistaPropiedad, "/propiedades/<int:id_propiedad>")
    api.add_resource(VistaReservas, "/propiedades/<int:id_propiedad>/reservas")
    api.add_resource(VistaReserva, "/reservas/<int:id_reserva>")
    api.add_resource(VistaMovimientos, "/propiedades/<int:id_propiedad>/movimientos")
    api.add_resource(VistaMovimiento, "/movimientos/<int:id_movimiento>")
    api.add_resource(VistaBancos, "/bancos")
    api.add_resource(VistaTipoUsuario, "/tipo-usuarios")
    api.add_resource(VistaTipoIdentificacion, "/tipo-identificacion")
    api.add_resource(VistaTipoMovimientos, "/tipo-movimientos")


app = create_flask_app()
db.init_app(app)
db.create_all()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    app.run()
