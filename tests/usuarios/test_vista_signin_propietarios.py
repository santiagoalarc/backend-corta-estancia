import json
import faker
from modelos import db, Propietario, TipoIdentificacion, TipoUsuario, Usuario
from faker import Faker

class TestVistaSignInPropietarios:

    def setUp(self):
        self.usuario = Usuario(usuario='test_user', contrasena='123456', tipo=TipoUsuario.ADMINISTRADOR)
        db.session.add(self.usuario)
        db.session.commit()


    def tearDown(self):
        db.session.rollback()
        Propietario.query.delete()
        Usuario.query.delete()
        

    def test_post_success(self, client):
        id_usuario = 1
        nombre = Faker().first_name()
        apellidos = Faker().last_name()
        tipo_identificacion = TipoIdentificacion.CEDULA_DE_CIUDADANIA.value
        identificacion = Faker().random_number(digits=10)
        correo = Faker().email()
        celular = Faker().random_number(digits=10)

        response = client.post(f'/signin/propietarios/{id_usuario}',json={
            'nombre': nombre,
            'apellidos': apellidos,
            'tipo_identificacion': tipo_identificacion,
            'identificacion': identificacion,
            'correo': correo,
            'celular': celular} ,headers={'Content-Type': 'application/json'})


        assert response.status_code == 201
        data = response.json
        assert data['mensaje'] == 'usuario tipo propietario creado'
        assert 'id' in data

    def test_post_duplicate(self, client):
        propietario = Propietario(id_usuario=Faker().random_number(digits=5), 
                                  nombre='John', 
                                  apellidos='Doe', 
                                  tipo_identificacion=TipoIdentificacion.CEDULA_DE_CIUDADANIA.value, 
                                  identificacion='12345', 
                                  correo='john@example.com', 
                                  celular='1234567890')
        db.session.add(propietario)
        db.session.commit()

        response = client.post(f'/signin/propietarios/{propietario.id_usuario}',json={
            'nombre': 'John',
            'apellidos': 'Doe',
            'tipo_identificacion': TipoIdentificacion.CEDULA_DE_CIUDADANIA.value,
            'identificacion': '12345',
            'correo': 'john@example.com',
            'celular': '123456789'},
            headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        data = response.json
        assert data['mensaje'] == 'Ya existe un propietario con esta informacion'

    def test_get(self, client):
        propietario = Propietario(id_usuario=1, 
                                  nombre='John', 
                                  apellidos='Doe', 
                                  tipo_identificacion=TipoIdentificacion.CEDULA_DE_CIUDADANIA.value, 
                                  identificacion='12345', 
                                  correo='john@example.com', 
                                  celular='1234567890')
        db.session.add(propietario)
        db.session.commit()

        response = client.get('/propietarios',headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
        assert len(data) == 1