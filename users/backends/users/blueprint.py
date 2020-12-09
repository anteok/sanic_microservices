from pydantic import ValidationError
from sanic import Blueprint
from sanic.exceptions import abort
from sanic.request import Request
from sanic.response import json, text
from sanic_openapi import doc

from db_connector import AsyncPSQLConnector
from backends.users.models import RegisterUserModel, AuthUserRequest, swg_registration, swg_auth, \
    SwgAuthUserResponse, SwgUserFullRecord
from backends.users.queries import get_user_info_by_id, create_user, auth_user


users_bp = Blueprint('Users service requests', url_prefix='/user')


@users_bp.listener('before_server_start')
async def setup_connection(app, loop):
    # There are should be a reliable connector, not that piece
    app.db = AsyncPSQLConnector(app.config['PSQL_URL']).db
    await app.db.connect()


@users_bp.listener('after_server_stop')
async def close_connection(app, loop):
    await app.db.disconnect()


@users_bp.route('/<user_id:string>/')
@doc.summary('User info')
@doc.description('Returns user info by its id')
@doc.produces(SwgUserFullRecord)
async def get_user_info(request: Request,  user_id: str):
    """
    Returns user full info by its user_id.
    """
    record = await get_user_info_by_id(request.app.db, user_id)
    if record is None:
        abort(404, f"No record with id {user_id}")
    return json(record.dict())


@users_bp.route('/registry/', methods=['POST'])
@doc.summary('User registration')
@doc.consumes(swg_registration, location='body')
@doc.description('Registers user with provided data')
@doc.response(201, {'message': 'Successful!'}, description='OK')
@doc.response(422, {'message': 'JSON validation error or user exists already'}, description='Unprocessable Entity')
async def register_user(request: Request):
    """
    Registers a new user.
    """
    try:
        user = RegisterUserModel(**request.json)
        await create_user(request.app.db, user)
        return text('OK', status=201)
    except (ValidationError, TypeError):
        abort(422, 'JSON validation error')
    except ValueError:
        abort(422, 'User already exists')


@users_bp.route('/auth/', methods=['POST'])
@doc.summary('User authorization')
@doc.consumes(swg_auth, location='body')
@doc.description('Authotizes user by username and password')
@doc.produces(SwgAuthUserResponse)
async def authorize_user(request: Request):
    """
    Authorizes user.
    """
    try:
        creds = await auth_user(request.app.db, AuthUserRequest(**request.json), request.app.config['SECRET'])
        if creds is None:
            abort(401, 'Wrong auth data')
        return json(creds.dict(), status=200)
    except (ValidationError, TypeError):
        abort(422, 'JSON validation error')
