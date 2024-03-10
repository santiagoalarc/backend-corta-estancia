from flask_jwt_extended import jwt_required
from flask_restful import Resource

from modelos import Usuario


class VistaUsuario(Resource):

    # get usuarios con roles
    @jwt_required()
    def get(self):
        # necesita manejar rol de usuario...
        propietarios = Usuario.query.all()
        return [{
            'nombre': p.administrador,
            'id': p.id,
            'tipo': p.tipo
        } for p in propietarios]
