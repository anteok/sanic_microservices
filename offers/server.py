import os

from sqlalchemy import create_engine

from backends.app import app
from backends.swagger.blueprint import swagger_bp
from backends.offers.blueprint import offers_bp


app.blueprint(offers_bp)
app.blueprint(swagger_bp)
app.config['PSQL_URL'] = os.getenv('PSQL_URL')
app.config['SECRET'] = os.getenv('SECRET_KEY')


engine = create_engine(app.config['PSQL_URL'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002)
