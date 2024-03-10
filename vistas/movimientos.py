from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from modelos import Movimiento, MovimientoSchema, Propiedad, db
from vistas.utils import buscar_propiedad
from sqlalchemy import exc, or_, and_

movimiento_schema = MovimientoSchema()


class VistaMovimientos(Resource):

    @jwt_required()
    def post(self, id_propiedad):
        propiedad = Propiedad.query.filter(and_(Propiedad.id == id_propiedad,
                                                or_(Propiedad.id_administrador == current_user.id,
                                                    Propiedad.id_usuario == current_user.id))).one_or_none()
        if not propiedad:
            return {
                'message': 'Propiedad no encontrada'
            }, 404

        try:
            movimiento = movimiento_schema.load(request.json, session=db.session)
            movimiento.id_propiedad = id_propiedad
            db.session.add(movimiento)
            db.session.commit()
        except ValidationError as validation_error:
            return validation_error.messages, 400
        except exc.IntegrityError:
            db.session.rollback()
            return {'mensaje': 'Hubo un error creando el movimiento. Revise los datos proporcionados'}, 400
        return movimiento_schema.dump(movimiento), 201

    @jwt_required()
    def get(self, id_propiedad):
        propiedad = Propiedad.query.filter(and_(Propiedad.id == id_propiedad,
                                                or_(Propiedad.id_administrador == current_user.id,
                                                    Propiedad.id_usuario == current_user.id))).one_or_none()

        if not propiedad:
            return {
                'mensaje': 'propiedad no encontrada'
            }, 404

        movimientos = db.session.query(Movimiento).join(Propiedad).filter(
            and_(Propiedad.id == id_propiedad,
                 or_(Propiedad.id_usuario == current_user.id,
                     Propiedad.id_administrador == current_user.id),
                 )).all()
        return movimiento_schema.dump(movimientos, many=True)
