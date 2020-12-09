import pytest
from bson import ObjectId
from hashlib import sha256

from backends.users.models import UserFullRecord, OfferRecord, RegisterUserModel
from backends.users.queries import get_user_info_by_id, create_user
from tests_.async_test_db import BaseAsyncDatabaseTest


class TestQueries(BaseAsyncDatabaseTest):

    @pytest.mark.asyncio
    async def test_get_user_by_id(self):
        assert await get_user_info_by_id(self.test_db, '1') is None

        await self.test_db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES ('1', 'test_user', 'password', 'test_email', 'deadbeef')
        """)

        record = await get_user_info_by_id(self.test_db, '1')
        assert isinstance(record, UserFullRecord)
        assert record.id == '1'
        assert record.username == 'test_user'
        assert record.password == 'password'
        assert record.email == 'test_email'
        assert record.salt == 'deadbeef'
        assert record.offers == []

        await self.test_db.execute("""
            INSERT INTO offers (id, user_id, title, text)
            VALUES ('1', '1', 'test_title', 'test_text')
        """)

        record = await get_user_info_by_id(self.test_db, '1')
        assert isinstance(record, UserFullRecord)
        assert record.id == '1'
        assert record.username == 'test_user'
        assert record.password == 'password'
        assert record.email == 'test_email'
        assert record.salt == 'deadbeef'
        assert isinstance(record.offers, list)
        assert len(record.offers) == 1

        offer_record = record.offers[0]
        assert isinstance(offer_record, OfferRecord)
        assert offer_record.offer_id == '1'
        assert offer_record.title == 'test_title'
        assert offer_record.text == 'test_text'

    @pytest.mark.asyncio
    async def test_create_user(self):
        await create_user(self.test_db, RegisterUserModel(username='name', password='pass', email='mail'))

        record = await self.test_db.fetch_one("SELECT * FROM users WHERE username = 'name'")
        assert ObjectId.is_valid(record['id'])
        assert record['username'] == 'name'
        assert record['salt'] == sha256(ObjectId(record['id']).binary).hexdigest()
        assert record['password'] == sha256(f"{record['salt']}pass".encode()).hexdigest()
        assert record['email'] == 'mail'
