import os

import jwt
import pytest
from bson import ObjectId
from hashlib import sha256

from backends.users.models import UserFullRecord, OfferRecord, RegisterUserModel, AuthUserRequest, AuthUserResponse
from backends.users.queries import get_user_info_by_id, create_user, auth_user
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
        await create_user(self.test_db, RegisterUserModel(username='test_user', password='pass', email='mail'))

        record = await self.test_db.fetch_one("SELECT * FROM users WHERE username = 'test_user'")
        assert ObjectId.is_valid(record['id'])
        assert record['username'] == 'test_user'
        assert record['salt'] == sha256(ObjectId(record['id']).binary).hexdigest()
        assert record['password'] == sha256(f"{record['salt']}pass".encode()).hexdigest()
        assert record['email'] == 'mail'

    @pytest.mark.asyncio
    async def test_auth_user(self):
        assert await auth_user(
            db=self.test_db,
            user=AuthUserRequest(username='test_user', password='pass'),
            secret=os.getenv('SECRET_KEY')
        ) is None

        user_id = str(ObjectId())
        hashed_pass = sha256(f'deadbeefpass'.encode()).hexdigest()
        await self.test_db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES (:id, 'test_user', :pass, 'test_email', 'deadbeef')
        """, values={'id': user_id, 'pass': hashed_pass})

        assert await auth_user(
            db=self.test_db,
            user=AuthUserRequest(username='test_user', password='wrong'),
            secret=os.getenv('SECRET_KEY')
        ) is None
        record = await auth_user(
            db=self.test_db,
            user=AuthUserRequest(username='test_user', password='pass'),
            secret=os.getenv('SECRET_KEY')
        )
        assert isinstance(record, AuthUserResponse)
        assert record.id == user_id
        assert jwt.decode(record.jwt, os.getenv('SECRET_KEY'), algorithms=['HS256']) == {'username': 'test_user'}
