from flask import jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from modelos import TipoIdentificacion


class VistaTipoIdentificacion(Resource):

    @cross_origin()
    def get(self):
        return jsonify([tipoIdentificacion.name for tipoIdentificacion in TipoIdentificacion])
