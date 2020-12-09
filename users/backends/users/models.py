from typing import List, Optional

from pydantic import BaseModel
from sanic_openapi import doc


class OfferRecord(BaseModel):
    offer_id: str
    title: str
    text: str


class UserFullRecord(BaseModel):
    id: str
    username: str
    password: str
    salt: str
    email: str
    offers: List[Optional[OfferRecord]]


class RegisterUserModel(BaseModel):
    username: str
    password: str
    email: str


class AuthUserRequest(BaseModel):
    username: str
    password: str


class AuthUserResponse(BaseModel):
    id: str
    jwt: str

# Certainly, a way to serialize objects and generate swagger docs must be universal.
# But I was not able to find it quickly, so I used separate classes according to sanic-openapi documentation.


swg_registration = doc.JsonBody({
    'username': doc.String('Name of user account'),
    'password': doc.String('Password of user account'),
    'email': doc.String('User email')
})

swg_auth = doc.JsonBody({
    'username': doc.String('Name of user account'),
    'password': doc.String('Password of user account'),
})


class SwgOfferRecord:
    offer_id = doc.String('Offer id')
    title = doc.String('Offer title')
    text = doc.String('Offer text')


class SwgUserFullRecord:
    id = doc.String('User id')
    username = doc.String('Name of user')
    password = doc.String('User\'s password')
    salt = doc.String('Cryptographic salt for saving password')
    email = doc.String('User email')
    offers: doc.List(items=SwgOfferRecord, description='Offers of current user')


class SwgAuthUserResponse:
    id = doc.String('User id')
    jwt = doc.String('JWT Token')
