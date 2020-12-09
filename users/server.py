import os

from sanic_openapi import swagger_blueprint
from sqlalchemy import create_engine

from backends.app import app
from backends.users.blueprint import users_bp


app.blueprint(users_bp)
app.blueprint(swagger_blueprint)
app.config['PSQL_URL'] = os.getenv('PSQL_URL')
app.config['SECRET'] = os.getenv('SECRET_KEY')


engine = create_engine(app.config['PSQL_URL'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
