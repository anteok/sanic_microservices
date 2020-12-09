from sanic import Blueprint
from sanic.exceptions import abort
from sanic.request import Request
from sanic.response import json

from backends.db_.db_connector import AsyncPSQLConnector
from backends.users.queries import get_user_info_by_id

db = None
users_bp = Blueprint('user_blueprint', url_prefix='/user')


@users_bp.listener('before_server_start')
async def setup_connection(app, loop):
    app.db = AsyncPSQLConnector(app.config['PSQL_URL']).db
    await app.db.connect()


@users_bp.listener('after_server_stop')
async def close_connection(app, loop):
    await app.db.disconnect()


@users_bp.route('/<user_id:string>/')
async def get_user_info(request: Request,  user_id: str):
    """
    Returns user full info by its user_id.
    """
    print(request.app.db)
    record = await get_user_info_by_id(request.app.db, user_id)
    if record is None:
        abort(404)
    return json(record.dict())
