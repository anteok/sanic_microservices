from pydantic import BaseModel
from sanic_openapi import doc


class CreateOfferRecord(BaseModel):
    user_id: str
    title: str
    text: str


class FullOfferRecord(BaseModel):
    id: str
    user_id: str
    title: str
    text: str


# Certainly, a way to serialize objects and generate swagger docs must be universal.
# But I was not able to find it quickly, so I used separate classes according to sanic-openapi documentation.


swg_post_offer = doc.JsonBody({
    'user_id': doc.String('User id'),
    'title': doc.String('Offer title'),
    'text': doc.String('Offer text')
})


class SwgFullOfferRecord:
    id = doc.String('Offer id')
    user_id = doc.String('User id')
    title = doc.String('Offer title')
    text = doc.String('Offer text')
