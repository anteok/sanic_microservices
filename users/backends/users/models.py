from typing import List, Optional

from pydantic import BaseModel


class OfferRecord(BaseModel):
    offer_id: str
    title: str
    text: str


class UserFullRecord(BaseModel):
    id: str
    username: str
    password: str
    email: str
    offers: List[Optional[OfferRecord]]
