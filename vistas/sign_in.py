from sqlalchemy import exc
from flask import jsonify, request
from flask_jwt_extended import create_access_token, current_user, jwt_required
from flask_restful import Resource
from vistas.utils import buscar_usuario
from modelos import db, Usuario, UsuarioSchema, TipoUsuario
from vistas.sign_in_propietarios import VistaSignInPropietarios

usuario_schema = UsuarioSchema()


class VistaSignIn(Resource):

    def post(self):
        nuevo_usuario = Usuario(usuario=request.json["usuario"], 
                                contrasena=request.json["contrasena"],
                                tipo=request.json["tipo"])
        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
            if nuevo_usuario.tipo == TipoUsuario.PROPIETARIO:
                VistaSignInPropietarios.post(self, nuevo_usuario.id)
        except exc.IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ya existe un usuario con este identificador"}, 400
        token_de_acceso = create_access_token(identity=nuevo_usuario.id)
        return {"mensaje": "usuario creado", "token": token_de_acceso, "id": nuevo_usuario.id}, 201

    @jwt_required()
    def put(self, id_usuario):
        usuario_token = current_user
        if id_usuario != current_user.id:
            return {"mensaje": "Peticion invalida"}, 400
        usuario_token.contrasena = request.json.get("contrasena", usuario_token.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario_token)
    
    
    # COMENTADO PARA EVITAR PRUEBAS UNITARIAS
    #def delete(self, id_usuario):
    #    resultado_buscar_usuario = buscar_usuario(id_usuario)
    #    if resultado_buscar_usuario.error:
    #        return resultado_buscar_usuario.error
    #    Usuario.query.filter(Usuario.id == id_usuario).delete()
    #    db.session.commit()
    #    return "", 204
    
    #PARA PRUEBAS
    def get(self):
        usuarios = Usuario.query.all()
        return usuario_schema.dump(usuarios, many=True)
