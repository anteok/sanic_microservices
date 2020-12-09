from typing import Optional

from databases import Database
from sqlalchemy import sql, and_

from backends.users.models import UserFullRecord, OfferRecord
from tables import offers, users


async def get_user_info_by_id(db: Database, user_id: str) -> Optional[UserFullRecord]:
    """
    Returns user record with offers.
    """
    ofs = offers.select().alias('ofs')
    request = sql.select([
        users.c.id,
        users.c.username,
        users.c.password,
        users.c.salt,
        users.c.email,
        ofs.c.id.label('offer_id'),
        ofs.c.title,
        ofs.c.text,
    ]).select_from(users.outerjoin(ofs, and_(users.c.id == ofs.c.user_id, users.c.id == user_id)))
    raw_data = await db.fetch_all(request)
    if not raw_data:
        return None
    if raw_data[0].get('offer_id'):
        return UserFullRecord(**raw_data[0], offers=[OfferRecord(**i) for i in raw_data])
    return UserFullRecord(**raw_data[0], offers=[])
