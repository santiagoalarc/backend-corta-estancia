from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from sqlalchemy import or_, and_

from modelos import Propiedad, PropiedadSchema, db, TipoUsuario, Propietario
from vistas.utils import buscar_propiedad

propiedad_schema = PropiedadSchema()


class VistaPropiedad(Resource):

    @jwt_required()
    def put(self, id_propiedad):
        resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
        if resultado_buscar_propiedad.error:
            return resultado_buscar_propiedad.error
        for key, value in request.json.items():
            setattr(resultado_buscar_propiedad.propiedad, key, value)
        db.session.commit()
        return propiedad_schema.dump(resultado_buscar_propiedad.propiedad)

    @jwt_required()
    def delete(self, id_propiedad):
        propiedad = Propiedad.query.filter(and_(Propiedad.id == id_propiedad,
                                                Propiedad.id_administrador == current_user.id)).one_or_none()

        if not propiedad:
            return {
                'mensaje': 'propiedad no encontrada para id admin y id propiedad'
            }, 404

        db.session.delete(propiedad)
        db.session.commit()
        return "", 204

    @jwt_required()
    def get(self, id_propiedad):
        propiedad_encontrada = buscar_propiedad(id_propiedad, current_user.id)
        if propiedad_encontrada.error:
            return propiedad_encontrada.error
        resultado_buscar_propiedad = propiedad_encontrada.propiedad
        
        propietario = Propietario.query.filter(
            Propietario.id_usuario == resultado_buscar_propiedad.id_usuario).one_or_none()

        if not propietario:
            buscar_propiedad.error = {'mensaje': 'propietario no encontrada'}, 404

        resultado_buscar_propiedad.nombre_propietario = propietario.nombre + ' ' + propietario.apellidos
        resultado_buscar_propiedad.numero_contacto = propietario.celular

        return propiedad_schema.dump(resultado_buscar_propiedad)
