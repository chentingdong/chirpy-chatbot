import pickle
from datetime import timedelta
from uuid import uuid4

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict

class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(obj):
            obj.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False

        # explicitly declaring them
        self.workflow = None


class RedisSessionInterface(SessionInterface):
    default_expiration_days = 1  # days
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis=None, prefix='illusionist'):
        """
        Construct redis session interface
        :param redis: redis client
        :param prefix: prefix key to store the session in redis
        """

        self.redis = redis
        self.prefix = prefix

    def get_redis_expiration_time(self, app, session):
        """
        Get the redis expiration time
        :param app: the flask app obj
        :param session: the session obj
        :return: the expiration time
        """
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=RedisSessionInterface.default_expiration_days)

    def get_session_id(self, request):
        sid = request.args.get('session_id', None)
        if not sid:
            request_json = request.get_json(silent=True)
            if request_json:
                sid = request_json.get('session_id', None)
        if not sid:
            sid = str(uuid4())
        return sid

    def delete_session(self, sid):
        return self.redis.delete(':'.join([self.prefix, sid]))

    def open_session(self, app, request):
        """
        Open the session
        :param app: the flask app obj
        :param request: the request obj
        :return: the session
        """
        sid = self.get_session_id(request)
        val = self.redis.get(':'.join([self.prefix, sid]))
        if val:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        """
        Save the session
        :param app: the flask app obj
        :param session: the session to save
        :param response: the response to generate
        :return:
        """
        if not session:
            self.redis.delete(':'.join([self.prefix + session.sid]))
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(':'.join([self.prefix, session.sid]), int(redis_exp.total_seconds()), val)
