import requests
from flask import session
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, make_transient

from python_utils.config import server_config
from python_utils.flask_sqlalchemy_base import db, ParametrizedMixin, AuditMixin, JsonDeSerMixin


class Agent(db.Model, ParametrizedMixin, AuditMixin, JsonDeSerMixin):
    __tablename__ = 'agent'
    __table_args__ = {'schema': 'illusionist'}

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200))
    description = Column(String(1000))
    editing_by = Column(String(128), nullable=True, default=None)
    app_id = Column(Integer, ForeignKey("admin_console.app.id"))
    settings = Column(JSON)
    state = Column(String)
    bots = association_proxy('agent_bots', 'bot')
    services = relationship("Service")

    def __init__(self, name='', description='', editing_by={}, app_id=0, params={}, settings={}, state='draft', **kwargs):
        self.name = name
        self.description = description
        self.editing_by = editing_by
        self.app_id = app_id
        self.settings = settings
        self.state = state
        if params:
            self.params = params
        else:
            ParametrizedMixin.__init__(self, kwargs)

    def __repr__(self):
        return 'Agent({})'.format(self.id)

    def get_id(self, **kwargs):
        return self.id

    def get_config(self, agent_id):
        agent_config = session.get('agent_config', {})
        if not agent_config:
            agent = Agent.query.filter_by(id=agent_id).first()
            agent_config = agent.parameters
            session.setdefault('agent_config', agent_config)
        return agent_config

    def clone(self):
        db.session.expunge(self)
        make_transient(self)
        self.id = None
        self.name = 'clone of ' + self.name
        db.session.add(self)
        db.session.commit()


class AgentsSimilarityMatrix(db.Model, JsonDeSerMixin, AuditMixin):
    __tablename__ = 'agents_similarity_matrix'

    matrix_id = Column(Integer, autoincrement=True)
    agent_id = Column(Integer, ForeignKey(Agent.id), primary_key=True)
    nlp = Column(String, primary_key=True)
    match_unit = Column(String, primary_key=True)
    matrix = Column(JSON)

    def __init__(self, agent_id='', **kwargs):
        self.agent_id = agent_id

    def update(self, nlp='spacy', match_unit='match_unit'):
        agent_id = self.agent_id
        luke_url = server_config['luke']['base_url']
        matrix_url = '{luke_url}/api/apps/{app_id}/similarity_matrix/{nlp}/{match_unit}'.format(**locals())
        response = requests.get(matrix_url)

        self.nlp = nlp
        self.match_unit = match_unit
        self.matrix = response.json()['similarity_matrix']

        db.session.merge(self)
        db.session.commit()