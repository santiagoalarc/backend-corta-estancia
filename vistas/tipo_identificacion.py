from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from modelos import TipoIdentificacion


class VistaTipoIdentificacion(Resource):

    def get(self):
        return jsonify([tipoIdentificacion.name for tipoIdentificacion in TipoIdentificacion])
