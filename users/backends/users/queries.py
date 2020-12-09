from typing import Optional

from bson import ObjectId
from databases import Database
from hashlib import sha256
from sqlalchemy import sql, and_

from backends.users.models import UserFullRecord, OfferRecord, RegisterUserModel
from tables import offers, users


async def get_user_info_by_id(db: Database, user_id: str) -> Optional[UserFullRecord]:
    """
    Returns user record with offers.
    """
    ofs = offers.select().alias('ofs')
    query = sql.select([
        users.c.id,
        users.c.username,
        users.c.password,
        users.c.salt,
        users.c.email,
        ofs.c.id.label('offer_id'),
        ofs.c.title,
        ofs.c.text,
    ]).select_from(users.outerjoin(ofs, and_(users.c.id == ofs.c.user_id, users.c.id == user_id)))
    raw_data = await db.fetch_all(query)
    if not raw_data:
        return None
    if raw_data[0].get('offer_id'):
        return UserFullRecord(**raw_data[0], offers=[OfferRecord(**i) for i in raw_data])
    return UserFullRecord(**raw_data[0], offers=[])


async def create_user(db: Database, user: RegisterUserModel) -> None:
    """
    Creates new user record
    """
    user_id = ObjectId()
    salt = sha256(user_id.binary).hexdigest()
    hashed_pass = sha256(f'{salt}{user.password}'.encode()).hexdigest()
    # email validation can be used too if we'll use correct model
    await db.execute(users.insert().values(
        id=str(user_id),
        username=user.username,
        password=hashed_pass,
        salt=salt,
        email=user.email
    ))
