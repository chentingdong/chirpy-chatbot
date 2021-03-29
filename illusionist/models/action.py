from collections import defaultdict

from sqlalchemy import Column, Integer, String, event
from sqlalchemy.ext.associationproxy import association_proxy

from python_utils.flask_sqlalchemy_base import db, JsonDeSerMixin, AuditMixin, VersionedMixin, ParametrizedMixin


def polymorphic_fallback(mapper_klass):
    event.listens_for(mapper_klass, 'mapper_configured')(receive_mapper_configured)
    return mapper_klass


def receive_mapper_configured(mapper, class_):
    mapper.polymorphic_map = defaultdict(lambda: mapper, mapper.polymorphic_map)


@polymorphic_fallback
class Action(db.Model, JsonDeSerMixin, AuditMixin, VersionedMixin, ParametrizedMixin):
    __tablename__ = 'action'
    __mapper_args__ = {
        'polymorphic_identity': 'Action',
        'polymorphic_on': 'action_type'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    description = Column(String(1000))
    action_type = Column(String(250))
    editing_by = Column(String(128), nullable=True, default=None)

    bots = association_proxy('action_bots', 'bot')

    def __init__(self, name='', description='', action_type='', params={}, version=1, **kwargs):
        self.name = name
        self.description = description
        self.action_type = action_type
        VersionedMixin.__init__(self, name=name, version=version)
        if params:
            self.params = params
        else:
            ParametrizedMixin.__init__(self, kwargs)

    def __repr__(self):
        return '{}({}, {})'.format(self.action_type, self.id, self.name)

    def run(self, context):
        raise NotImplementedError
