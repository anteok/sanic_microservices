import os

import bson
import jwt
import pytest
from hashlib import sha256

from bson import ObjectId
from sanic import Sanic
from sqlalchemy import create_engine

from backends.users.blueprint import users_bp
from tables import metadata


class BaseAppTest:

    @pytest.fixture(autouse=True, scope="function")
    async def init_db(self):
        """
        Initiates test db.
        """
        engine = create_engine(os.getenv('PSQL_TEST_URL'))
        metadata.drop_all(engine)
        metadata.create_all(engine)
        yield
        metadata.drop_all(engine)

    @pytest.fixture(autouse=True, scope="function")
    async def test_app(self):
        """
        Fixture for initial app setup.
        """
        app = Sanic(__name__)
        app.config['PSQL_URL'] = os.getenv('PSQL_TEST_URL')
        app.config['SECRET'] = os.getenv('SECRET_KEY')
        app.blueprint(users_bp)

        yield app

    @pytest.fixture
    def test_cli(self, loop, test_app, sanic_client):
        return loop.run_until_complete(sanic_client(test_app))


class TestUserRoutes(BaseAppTest):

    async def test_get_user_info_request(self, test_cli):
        user_id = str(bson.ObjectId())
        salt = sha256(b'some').hexdigest()
        response = await test_cli.get(f'/user/{user_id}/')
        assert response.status == 404

        await test_cli._app.db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES (:user_id, 'test_user', 'password', 'test_email', :salt)
        """, values={'user_id': user_id, 'salt': salt})

        response = await test_cli.get(f'/user/{user_id}/')

        assert response.status == 200
        assert await response.json() == {
            'id': user_id,
            'username': 'test_user',
            'password': 'password',
            'email': 'test_email',
            'salt': salt,
            'offers': [],
        }

    async def test_post_register_user(self, test_cli):
        response = await test_cli.post(f'/user/registry/')
        assert response.status == 422
        response = await test_cli.post(f'/user/registry/', json={'username': 'name', 'password': 'pass'})
        assert response.status == 422

        response = await test_cli.post(
            uri=f'/user/registry/',
            json={'username': 'name', 'password': 'pass', 'email': 'mail'}
        )
        assert response.status == 201

        record = await test_cli._app.db.fetch_one("SELECT * FROM users WHERE username = 'name'")
        assert ObjectId.is_valid(record['id'])
        assert record['username'] == 'name'
        assert record['salt'] == sha256(ObjectId(record['id']).binary).hexdigest()
        assert record['password'] == sha256(f"{record['salt']}pass".encode()).hexdigest()
        assert record['email'] == 'mail'

    async def test_post_auth_user(self, test_cli):
        response = await test_cli.post(f'/user/auth/')
        assert response.status == 422
        response = await test_cli.post(f'/user/auth/', json={'username': 'test_user'})
        assert response.status == 422

        user_id = str(ObjectId())
        hashed_pass = sha256(f'deadbeefpass'.encode()).hexdigest()
        await test_cli._app.db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES (:id, 'test_user', :pass, 'test_email', 'deadbeef')
        """, values={'id': user_id, 'pass': hashed_pass})

        response = await test_cli.post(f'/user/auth/', json={'username': 'test_user', 'password': 'wrong'})
        assert response.status == 401
        response = await test_cli.post(f'/user/auth/', json={'username': 'wrong', 'password': 'pass'})
        assert response.status == 401

        response = await test_cli.post(f'/user/auth/', json={'username': 'test_user', 'password': 'pass'})
        assert response.status == 200
        data = await response.json()
        assert data.get('id')
        assert data['id'] == user_id
        assert data.get('jwt')
        assert jwt.decode(data['jwt'], test_cli._app.config['SECRET'], algorithms=['HS256']) == \
               {'username': 'test_user'}
