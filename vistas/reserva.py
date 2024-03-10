from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from modelos import Movimiento, Reserva, ReservaSchema, db
from vistas.utils import buscar_reserva

reserva_schema = ReservaSchema()

class VistaReserva(Resource):

    @jwt_required()
    def put(self, id_reserva):
        resultado_buscar_reserva = buscar_reserva(id_reserva, current_user.id)
        if resultado_buscar_reserva.error:
            return resultado_buscar_reserva.error
        reserva_schema.load(request.json, session=db.session, instance=resultado_buscar_reserva.reserva, partial=True)
        db.session.commit() 
        return reserva_schema.dump(resultado_buscar_reserva.reserva)
    
    @jwt_required()
    def delete(self, id_reserva):
        resultado_buscar_reserva = buscar_reserva(id_reserva, current_user.id)
        if resultado_buscar_reserva.error:
            return resultado_buscar_reserva.error
        Reserva.query.filter(Reserva.id == id_reserva).delete()
        Movimiento.query.filter(Movimiento.id_reserva == id_reserva).delete()
        db.session.commit()
        return "", 204
    
    @jwt_required()
    def get(self, id_reserva):
        resultado_buscar_reserva = buscar_reserva(id_reserva, current_user.id)
        if resultado_buscar_reserva.error:
            return resultado_buscar_reserva.error
        return reserva_schema.dump(resultado_buscar_reserva.reserva)
