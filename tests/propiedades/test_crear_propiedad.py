import json

from flask_jwt_extended import create_access_token
from modelos import Banco, Usuario, Propiedad, db, TipoUsuario


class TestCrearPropiedad:

    def setup_method(self):
        self.administrador = Usuario(usuario='test_admin', contrasena='123456', tipo=TipoUsuario.ADMINISTRADOR)
        db.session.add(self.administrador)
        db.session.commit()
        self.propietario_1 = Usuario(usuario='test_owner_1', contrasena='habia', tipo=TipoUsuario.PROPIETARIO)
        db.session.add(self.propietario_1)
        db.session.commit()
        self.propietario_2 = Usuario(usuario='test_owner_2', contrasena='una-vez', tipo=TipoUsuario.PROPIETARIO)
        db.session.add(self.propietario_2)
        db.session.commit()
        self.administrador_token = create_access_token(identity=self.administrador.id)
        self.propietario_1_token = create_access_token(identity=self.propietario_1.id)
        self.propietario_2_token = create_access_token(identity=self.propietario_2.id)

        self.datos_propiedad = {
            'nombre_propiedad': 'Refugio el lago',
            'ciudad': 'Boyaca',
            'municipio': 'Paipa',
            'direccion': 'Vereda Toibita',
            'id_usuario': f'{self.propietario_1.id}',
            'id_administrador': f'{self.administrador.id}',
            'banco': Banco.BANCO_BBVA.value,
            'numero_cuenta': '3123334455',
        }

    def teardown_method(self):
        db.session.rollback()
        Usuario.query.delete()
        Propiedad.query.delete()

    def enviar_peticion(self, client, data: dict = None, token: str = None, peticion=None):
        json_request_data = data or self.datos_propiedad
        json_data = json.dumps(json_request_data)
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        if not peticion:
            self.respuesa = client.post('/propiedades', data=json_data, headers=headers)
        else:
            self.respuesa = peticion('/propiedades', data=json_data, headers=headers)
        self.respuesta_json = self.respuesa.json

    def test_retorna_201_si_es_exitoso(self, client):
        self.enviar_peticion(client, token=self.administrador_token)
        assert self.respuesa.status_code == 201

    def test_retorna_dict_si_es_exitoso(self, client):
        self.enviar_peticion(client, token=self.administrador_token)
        assert isinstance(self.respuesta_json, dict)

    def test_retorna_401_si_token_no_es_enviado(self, client):
        self.enviar_peticion(client)
        assert self.respuesa.status_code == 401

    def test_propiedad_es_creada_en_db(self, client):
        self.enviar_peticion(token=self.administrador_token, client=client)
        propiedades_en_db = Propiedad.query.all()
        assert len(propiedades_en_db) == 1
        assert self.respuesta_json["id"] == propiedades_en_db[0].id

    def test_propiedad_es_creada_para_propietario_por_administrador_logeado(self, client):
        self.enviar_peticion(token=self.administrador_token, client=client)
        propiedad_db = Propiedad.query.filter(Propiedad.id_administrador == self.administrador.id).first()
        assert propiedad_db

    def test_propiedades_son_listadas_por_administrador(self, client):
        # crear propiedad por defecto
        self.enviar_peticion(token=self.administrador_token, client=client)
        assert self.respuesta_json
        # crear una nueva propiedad adicional
        self.enviar_peticion(token=self.administrador_token, data={
            'nombre_propiedad': 'La Maritima',
            'ciudad': 'Tunja',
            'municipio': 'Boyaca',
            'direccion': 'Transversal de la Maritima',
            'id_usuario': self.propietario_2.id,
            'id_administrador': self.administrador.id,
            'banco': Banco.BANCO_BBVA.value,
            'numero_cuenta': '3123334455',
        }, client=client)
        assert self.respuesta_json

        # obtener lista de propiedades vistas desde la vista del admin
        self.enviar_peticion(token=self.administrador_token, data={}, client=client, peticion=client.get)

        assert isinstance(self.respuesta_json, list)
        assert len(self.respuesta_json) == 2

    def test_propiedades_son_listadas_por_propietario(self, client):
        # crear propiedad por defecto
        self.enviar_peticion(token=self.administrador_token, client=client)
        assert self.respuesta_json
        # crear una nueva propiedad adicional
        self.enviar_peticion(token=self.administrador_token, data={
            'nombre_propiedad': 'El Lago Dorado',
            'ciudad': 'Tunja',
            'municipio': 'Boyaca',
            'direccion': 'Transversal de la Miritima',
            'id_usuario': self.propietario_2.id,
            'id_administrador': self.administrador.id,
            'banco': Banco.BANCO_BBVA.value,
            'numero_cuenta': '3123334455',
        }, client=client)
        assert self.respuesta_json

        # obtener lista de propiedades vistas desde la vista del admin
        self.enviar_peticion(token=self.propietario_2_token, data={}, client=client, peticion=client.get)

        assert isinstance(self.respuesta_json, list)
        assert len(self.respuesta_json) == 1
        assert self.respuesta_json[0]['nombre_propiedad'] == 'El Lago Dorado'
        assert self.respuesta_json[0]['id_usuario'] == self.propietario_2.id
        assert self.respuesta_json[0]['id_administrador'] == self.administrador.id

    def test_retorna_campos_esperados(self, client):
        self.enviar_peticion(token=self.administrador_token, client=client)

        assert 'nombre_propiedad' in self.respuesta_json
        assert 'ciudad' in self.respuesta_json
        assert 'municipio' in self.respuesta_json
        assert 'direccion' in self.respuesta_json
        assert 'banco' in self.respuesta_json
        assert 'numero_cuenta' in self.respuesta_json
        assert 'id_usuario' in self.respuesta_json
        assert 'id_administrador' in self.respuesta_json
