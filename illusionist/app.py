import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

import datetime
from flask import Flask
from flask_request_id import RequestID
from flask_cors import CORS
from python_utils.config import server_config
from python_utils.redis_store import redis
from python_utils.redis_session import RedisSessionInterface
from python_utils.logger import logger, logger_file, logger_console
from python_utils.flask_sqlalchemy_base import db
from python_utils.helpers import get_version


def create_app():
    app = Flask(__name__)

    app.config['DEBUG'] = server_config['configs']['debug']
    app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    illusionist_config = server_config['mysql']['illusionist']
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{password}@{host}/{database}'.format(
        **illusionist_config)

    admin_console = server_config['mysql']['console']
    app.config['SQLALCHEMY_BINDS'] = {'console': 'mysql+pymysql://{user}:{password}@{host}/{database}'.format(
        **admin_console)}

    app.config['SQLALCHEMY_POOL_SIZE'] = server_config['sqlalchemy']['default_pool_size']
    app.config['SQLALCHEMY_POOL_RECYCLE'] = server_config['sqlalchemy']['default_pool_recycle']
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = server_config['sqlalchemy']['default_pool_timeout']
    app.config['SQLALCHEMY_POOL_PRE_PING'] = server_config['sqlalchemy']['default_pool_pre_ping']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = server_config['sqlalchemy']['track_modifications']

    # don't automatically sort keys, it can be ordered dict that we want to keep order.
    app.config["JSON_SORT_KEYS"] = False

    # Flask-JWT
    app.config['JWT_SECRET_KEY'] = 'ASTOUNDING'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=3)

    # redis
    prefix = server_config['redis']['prefix']
    app.session_interface = RedisSessionInterface(redis=redis, prefix=prefix)

    # enable cross origin resource sharing
    CORS(app, resources={
        r'/api/*': {'origins': '*'},
        r'/user/*': {'origins': '*'},
        r'/flasgger': {'origins': '*'}
    })
    # CORS(app)

    # request-id
    RequestID(app, header_name="Request-Id")

    db.init_app(app)

    @app.before_first_request
    def reinit():
        """
        reinit logging and impala connection so each gunicorn thread get one.
        :return:
        """
        logger.reinit()
        # impala_global.reconnect()

    from illusionist.apis import api_manager, bp
    with app.app_context():
        api_manager.init_app(app, session=db.session)

    # the following import line is needed to register all the routes on the default illuisonist blueprint
    from illusionist.apis import ask, agent, bot, event, reporting, server, swagger, user
    app.register_blueprint(bp.bp)

    from illusionist.apis.user import jwt, bcrypt
    jwt.init_app(app)
    bcrypt.init_app(app)

    logger_file.info('Starting illusionist server')
    logger_console.info('Starting illusionist server {}'.format(get_version()))

    return app
