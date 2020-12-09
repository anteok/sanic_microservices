import os
from uuid import uuid4

import pytest
from bson import ObjectId
from sanic import Sanic
from sqlalchemy import create_engine

from backends.offers.blueprint import offers_bp
from backends.offers.queries import uuid_valid
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
        app.blueprint(offers_bp)

        yield app

    @pytest.fixture
    def test_cli(self, loop, test_app, sanic_client):
        return loop.run_until_complete(sanic_client(test_app))


class TestUserRoutes(BaseAppTest):

    async def test_post_offer(self, test_cli):
        response = await test_cli.post(f'/offer/create/')
        assert response.status == 422
        response = await test_cli.post(f'/offer/create/', json={'user_id': '1', 'title': 'title'})
        assert response.status == 422

        response = await test_cli.post(f'/offer/create/', json={'user_id': '1', 'title': 'title', 'text': 'text'})
        assert response.status == 422

        await test_cli._app.db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES ('1', 'test_user', 'password', 'test_email', 'deadbeef')
        """)
        response = await test_cli.post(f'/offer/create/', json={'user_id': '1', 'title': 'title', 'text': 'text'})
        assert response.status == 201

        record = await test_cli._app.db.fetch_one("SELECT * FROM offers WHERE user_id = '1'")

        assert uuid_valid(record['id'])
        assert record['user_id'] == '1'
        assert record['title'] == 'title'
        assert record['text'] == 'text'

        response = await test_cli.post(f'/offer/create/', json={'user_id': '1', 'title': 'title', 'text': 'text'})
        assert response.status == 201
        assert await test_cli._app.db.fetch_val(
            query="SELECT count(id) FROM offers WHERE user_id = '1'",
            column='count'
        ) == 2

    async def test_post_find_offers(self, test_cli):
        response = await test_cli.post(f'/offer/')
        assert response.status == 200
        assert await response.json() == []

        response = await test_cli.post(f'/offer/?user_id=1')
        assert response.status == 200
        assert await response.json() == []

        user_id = str(ObjectId())
        offer_id = str(uuid4())
        response = await test_cli.post(f'/offer/?offer_id={offer_id}')
        assert response.status == 200
        assert await response.json() == []
        response = await test_cli.post(f'/offer/?user_id={user_id}')
        assert response.status == 200
        assert await response.json() == []

        await test_cli._app.db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES (:id, 'test_user', 'password', 'test_email', 'deadbeef')
        """, values={'id': user_id})
        await test_cli._app.db.execute("""
            INSERT INTO offers (id, user_id, title, text)
            VALUES (:offer_id, :user_id, 'test_title', 'test_text')
        """, values={'offer_id': offer_id, 'user_id': user_id})

        response = await test_cli.post(f'/offer/?user_id={user_id}')
        assert response.status == 200
        assert await response.json() == [{
            'id': offer_id,
            'user_id': user_id,
            'title': 'test_title',
            'text': 'test_text',
        }]

        response = await test_cli.post(f'/offer/?offer_id={offer_id}')
        assert response.status == 200
        assert await response.json() == {
            'id': offer_id,
            'user_id': user_id,
            'title': 'test_title',
            'text': 'test_text',
        }