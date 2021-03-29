import string
import random

from flask import session
from sqlalchemy.orm import relationship

from python_utils.flask_sqlalchemy_base import ParametrizedMixin, AuditMixin, JsonDeSerMixin, db
from sqlalchemy import Column, Integer, String, JSON


class App(db.Model, ParametrizedMixin, AuditMixin, JsonDeSerMixin):
    __bind_key__ = 'console'
    __tablename__ = 'app'
    __table_args__ = {'schema': 'admin_console'}

    id = Column(Integer, autoincrement=True, primary_key=True)
    org_id = Column(Integer)
    name = Column(String(200))
    description = Column(String(1000))
    editing_by = Column(String(128), nullable=True, default=None)
    type = Column(String(10))
    uid = Column(String(8))
    settings = Column(JSON)

    agents = relationship("Agent")

    def __init__(self, name='', description='', type='', params={}, uid='', org_id=None, settings={}, **kwargs):
        self.name = name
        self.description = description
        self.type = type
        self.uid = self.random_generator()
        self.org_id = org_id
        self.settings = settings
        if params:
            self.params = params
        else:
            ParametrizedMixin.__init__(self, kwargs)

    def __repr__(self):
        return 'App({})'.format(self.id)

    def get_id(self, **kwargs):
        return self.id

    def get_config(self, app_id):
        app_config = session.get('app_config', {})
        if not app_config:
            app = App.query.filter_by(id=app_id).first()
            app_config = app.parameters
            session.setdefault('app_config', app_config)
        return app_config

    def random_generator(self, size=8, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))


