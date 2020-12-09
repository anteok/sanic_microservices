from uuid import uuid4

import pytest
from async_test_db import BaseAsyncDatabaseTest
from bson import ObjectId

from backends.offers.models import CreateOfferRecord, FullOfferRecord
from backends.offers.queries import create_offer, uuid_valid, get_offers_by_user_id, get_offer_by_id


class TestQueries(BaseAsyncDatabaseTest):

    @pytest.mark.asyncio
    async def test_create_offer(self):
        with pytest.raises(ValueError):
            assert await create_offer(self.test_db, CreateOfferRecord(user_id='1', title='title', text='text')) is None

        await self.test_db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES ('1', 'test_user', 'password', 'test_email', 'deadbeef')
        """)
        await create_offer(self.test_db, CreateOfferRecord(user_id='1', title='title', text='text'))
        record = await self.test_db.fetch_one("SELECT * FROM offers WHERE user_id = '1'")
        assert uuid_valid(record['id'])
        assert record['title'] == 'title'
        assert record['text'] == 'text'
        assert record['user_id'] == '1'

    @pytest.mark.asyncio
    async def test_get_offers_by_user_id(self):
        with pytest.raises(ValueError):
            assert await get_offers_by_user_id(self.test_db, '1')

        user_id = str(ObjectId())
        assert await get_offers_by_user_id(self.test_db, user_id) == []

        await self.test_db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES (:id, 'test_user', 'password', 'test_email', 'deadbeef')
        """, values={'id': user_id})
        await self.test_db.execute("""
            INSERT INTO offers (id, user_id, title, text)
            VALUES ('1', :id, 'test_title', 'test_text')
        """, values={'id': user_id})
        data = await get_offers_by_user_id(self.test_db, user_id)
        assert isinstance(data, list)
        assert len(data) == 1
        assert isinstance(data[0], FullOfferRecord)
        assert data[0].id == '1'

    @pytest.mark.asyncio
    async def test_get_offer_by_id(self):
        with pytest.raises(ValueError):
            assert await get_offer_by_id(self.test_db, '1')
        offer_id = str(uuid4())
        with pytest.raises(ValueError):
            assert await get_offer_by_id(self.test_db, offer_id)

        await self.test_db.execute("""
            INSERT INTO users (id, username, password, email, salt)
            VALUES ('1', 'test_user', 'password', 'test_email', 'deadbeef')
        """)
        await self.test_db.execute("""
            INSERT INTO offers (id, user_id, title, text)
            VALUES (:id, '1', 'test_title', 'test_text')
        """, values={'id': offer_id})
        data = await get_offer_by_id(self.test_db, offer_id)
        assert isinstance(data, FullOfferRecord)
        assert data.id

