import os

import bson
import pytest
from hashlib import sha256
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
