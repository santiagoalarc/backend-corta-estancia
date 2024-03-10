import datetime
from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from sqlalchemy import and_, or_

from modelos import Movimiento, MovimientoSchema, db, Propiedad
from vistas.utils import buscar_movimiento

movimiento_schema = MovimientoSchema()


class VistaMovimiento(Resource):

    @jwt_required()
    def put(self, id_movimiento):
        movimiento = Movimiento.query.filter(Movimiento.id == id_movimiento).one_or_none()

        if not movimiento:
            return {'mensaje': 'Movimiento no encontrado'}, 404

        propiedad = Propiedad.query.filter(and_(
            Propiedad.id == movimiento.id_propiedad,
            or_(Propiedad.id_usuario == current_user.id,
                Propiedad.id_administrador == current_user.id)
        )).one_or_none()

        if not propiedad:
            return {'mensaje': 'Movimiento no esta relacionado al usuario logeado'}, 404

        if not self.es_posible_eliminar_actualizar_movimiento(movimiento):
            return {
                'mensaje': 'No es posible actualizar este movimiento porque esta relacionado con una propiedad'
            }, 400

        movimiento_schema.load(request.json, session=db.session, instance=movimiento, partial=True)
        db.session.commit()
        return movimiento_schema.dump(movimiento)

    @jwt_required()
    def delete(self, id_movimiento):
        movimiento, propiedad = self.get_movimiento_y_propiedad(id_movimiento)

        if not propiedad:
            return {'mensaje': 'Movimiento no esta relacionado al usuario logeado'}, 404

        if not self.es_posible_eliminar_actualizar_movimiento(movimiento) or movimiento.id_reserva:
            return {
                'mensaje': 'Para eliminar este movimiento, debe eliminar la reserva asociada'
            }, 400

        db.session.delete(movimiento)
        db.session.commit()
        return "", 204

    @jwt_required()
    def get(self, id_movimiento):
        movimiento, propiedad = self.get_movimiento_y_propiedad(id_movimiento)

        if not propiedad:
            return {'mensaje': 'Movimiento no esta relacionado al usuario logeado'}, 404

        if not movimiento:
            return {'mensaje': 'Movimiento no relacionado al usuario'}, 404

        return movimiento_schema.dump(movimiento)

    def get_movimiento_y_propiedad(self, id_movimiento):
        movimiento = Movimiento.query.filter(Movimiento.id == id_movimiento).one_or_none()
        propiedad = Propiedad.query.filter(and_(
            Propiedad.id == movimiento.id_propiedad,
            or_(Propiedad.id_usuario == current_user.id,
                Propiedad.id_administrador == current_user.id)
        )).one_or_none()
        return movimiento, propiedad

    def es_posible_eliminar_actualizar_movimiento(self, movimiento):
        if movimiento.fecha.month < datetime.datetime.now().month:
            return False
        return True
