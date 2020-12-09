from db_connector import AsyncPSQLConnector
from pydantic import ValidationError
from sanic import Blueprint
from sanic.exceptions import abort
from sanic.request import Request
from sanic.response import text, json
from sanic_openapi import doc

from backends.offers.models import CreateOfferRecord, swg_post_offer, SwgFullOfferRecord
from backends.offers.queries import create_offer, get_offers_by_user_id, get_offer_by_id

offers_bp = Blueprint('Offers service requests', url_prefix='/offer')


@offers_bp.listener('before_server_start')
async def setup_connection(app, loop):
    app.db = AsyncPSQLConnector(app.config['PSQL_URL']).db
    await app.db.connect()


@offers_bp.listener('after_server_stop')
async def close_connection(app, loop):
    await app.db.disconnect()


@offers_bp.route('/create/', methods=['POST'])
@doc.summary('Create an offer')
@doc.consumes(swg_post_offer, location='body')
@doc.description('Creates offer attached to user by his id')
@doc.response(201, {'message': 'Successful!'}, description='OK')
@doc.response(422, {'message': 'JSON validation error or user does not exist'}, description='Unprocessable Entity')
async def create_new_offer(request: Request):
    """
    Returns user full info by its user_id.
    """
    try:
        await create_offer(request.app.db, CreateOfferRecord(**request.json))
        return text('OK', status=201)
    except (ValidationError, TypeError):
        abort(422, 'JSON validation error')
    except ValueError:
        abort(422, 'No user with that id')


@offers_bp.route('/', methods=['POST'])
@doc.summary('Offers data')
@doc.description('Returns offer data by offer_id or user_id')
@doc.consumes(doc.String(name='offer_id'), location='query')
@doc.consumes(doc.String(name='user_id'), location='query')
@doc.produces(SwgFullOfferRecord)
async def get_offers(request: Request):
    """
    Registers a new user.
    """
    # I just believe there are no cases when both user_id and offer_id are provided.
    # Otherwise only offer_id will be used.
    data = []
    try:
        if request.args.get('offer_id'):
            data = (await get_offer_by_id(request.app.db, request.args['offer_id'][0])).dict()
        elif request.args.get('user_id'):
            data = [i.dict() for i in await get_offers_by_user_id(request.app.db, request.args['user_id'][0])]
    except ValueError:
        pass
    return json(data)
