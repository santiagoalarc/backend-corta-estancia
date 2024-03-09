from sqlalchemy import exc
from flask import request, jsonify
from flask_jwt_extended import create_access_token, current_user, jwt_required
from flask_restful import Resource

from modelos import db, Propietario, PropietarioSchema
import vistas.sign_in

propietario_schema = PropietarioSchema()


class VistaSignInPropietarios(Resource):

    def post(self, id_usuario):
        nuevo_propietario = Propietario(id_usuario= id_usuario, 
                                        nombre= request.json["nombre"], 
                                        apellidos=request.json["apellidos"],
                                        tipo_identificacion=request.json["tipo_identificacion"],
                                        identificacion=request.json["identificacion"],
                                        correo=request.json["correo"],
                                        celular=request.json["celular"])
        db.session.add(nuevo_propietario)
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ya existe un propietario con esta informacion"}, 400
        return {"mensaje": "usuario tipo propietario creado", "id": nuevo_propietario.id}, 201
        
    #PARA PRUEBAS
    def get(self):
        usuarios = Propietario.query.all()
        return propietario_schema.dump(usuarios, many= True)

