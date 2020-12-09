from typing import Optional, Union, List
from uuid import uuid4, UUID

from asyncpg import ForeignKeyViolationError
from bson import ObjectId
from databases import Database
from tables import offers

from backends.offers.models import CreateOfferRecord, FullOfferRecord


def uuid_valid(value: str) -> bool:
    """
    Checks if value is a valid uuid4.
    """
    try:
        uuid_obj = UUID(value)
    except ValueError:
        return False
    return str(uuid_obj) == value


async def create_offer(db: Database, offer: CreateOfferRecord) -> None:
    """
    Creates new user offer.
    """
    offer_id = uuid4()
    try:
        async with db.transaction():
            await db.execute(offers.insert().values(
                id=str(offer_id),
                user_id=offer.user_id,
                title=offer.title,
                text=offer.text
            ))
    except ForeignKeyViolationError:
        raise ValueError


async def get_offers_by_user_id(db: Database, user_id: str) -> List[Optional[FullOfferRecord]]:
    """
    Returns all user offers.
    """
    if ObjectId.is_valid(user_id):
        return [FullOfferRecord(**i) for i in await db.fetch_all(offers.select().where(offers.c.user_id == user_id))]
    raise ValueError


async def get_offer_by_id(db: Database, offer_id: str) -> FullOfferRecord:
    """
    Returns offer data by its id.
    """
    if uuid_valid(offer_id):
        record = await db.fetch_one(offers.select().where(offers.c.id == offer_id))
        if record is None:
            raise ValueError
        return FullOfferRecord(**record)
    raise ValueError
