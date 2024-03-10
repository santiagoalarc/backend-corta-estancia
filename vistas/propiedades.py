from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import exc
import traceback
from sqlalchemy import or_

from modelos import Propiedad, db, PropiedadSchema, TipoUsuario

propiedad_schema = PropiedadSchema()


class VistaPropiedades(Resource):

    @jwt_required()
    def post(self):
        try:
            propiedad = propiedad_schema.load(request.json, session=db.session)
            if current_user.tipo == TipoUsuario.ADMINISTRADOR:
                propiedad.id_administrador = current_user.id
            db.session.add(propiedad)
            db.session.commit()
        except ValidationError as validation_error:
            print(traceback.format_exc())
            return validation_error.messages, 400
        except exc.IntegrityError as e:
            print(traceback.format_exc())
            db.session.rollback()
            return {'mensaje': 'Hubo un error creando la propiedad. Revise los datos proporcionados'}, 400
        return propiedad_schema.dump(propiedad), 201

    @jwt_required()
    def get(self):
        propiedades = Propiedad.query.filter(or_(Propiedad.id_usuario == current_user.id,
                                             Propiedad.id_administrador == current_user.id))
        return propiedad_schema.dump(propiedades, many=True)
