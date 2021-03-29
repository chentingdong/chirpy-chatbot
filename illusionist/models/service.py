from sqlalchemy.orm import make_transient
from python_utils.flask_sqlalchemy_base import db, JsonDeSerMixin, AuditMixin, VersionedMixin, ParametrizedMixin
from python_utils.logger import logger_console
from sqlalchemy import Column, Integer, String, Text, ForeignKey


class Service(db.Model, JsonDeSerMixin, AuditMixin, VersionedMixin, ParametrizedMixin):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), primary_key=True)
    description = Column(Text)
    agent_id = Column(Integer, ForeignKey("illusionist.agent.id"), primary_key=True)
    editing_by = Column(String(128), nullable=True, default=None)

    def __init__(self, name='', agent_id='', description='', params={}, version=1, **kwargs):
        self.name = name
        self.description = description
        self.agent_id = agent_id
        VersionedMixin.__init__(self, name=name, version=version)
        if params:
            self.params = params
        else:
            ParametrizedMixin.__init__(self, kwargs)

    def __repr__(self):
        return 'id:{}, name:{}, agent_id:{}'.format(self.id, self.name, self.agent_id)

    def find_by_name(self, service_name):
        try:
            service = self.query.filter_by(name=service_name).filter_by(agent_id=self.agent_id).first()
        except Exception as e:
            logger_console.warn("Failed finding service {}, {}".format(service_name, e))
        return service

    def get_params(self, agent_id, name):
        service = Service.query.filter_by(agent_id=agent_id, name=name).one_or_none()
        return service.params

    # TODO: Check if this can be handled any other way
    def find_by_name_and_agent_id(self, service_name, agent_id):
        try:
            service = self.query.filter_by(name=service_name).filter_by(agent_id=agent_id).first()
        except Exception as e:
            logger_console.warn("Failed finding service {}, {}".format(service_name, e))
        return service

    def clone(self, agent=None):
        service_exist = Service.query.filter_by(name=self.name, agent_id=agent.id).one_or_none()
        if service_exist:
            return

        db.session.expunge(self)
        make_transient(self)
        self.id = None
        self.agent_id = agent.id
        self.name = self.name
        db.session.add(self)
        db.session.commit()
