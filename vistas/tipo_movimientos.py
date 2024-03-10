from flask import jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from modelos import TipoMovimiento


class VistaTipoMovimientos(Resource):

    @jwt_required()
    @cross_origin()
    def get(self):
        return jsonify([tipo_movimiento.name for tipo_movimiento in TipoMovimiento])
