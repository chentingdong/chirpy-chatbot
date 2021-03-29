import json
from sqlalchemy.event import listen
from sqlalchemy import Column, Integer, String, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, make_transient
from python_utils.flask_sqlalchemy_base import db, ParametrizedMixin, AuditMixin, JsonDeSerMixin, VersionedMixin


class Bot(db.Model, VersionedMixin, ParametrizedMixin, AuditMixin, JsonDeSerMixin):
    __tablename__ = 'bot'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(128))
    description = Column(Text)
    enabled = Column(Boolean, nullable=False, default=1)
    searchable = Column(Boolean, nullable=False, default=1)
    editing_by = Column(String(128), nullable=True, default=None)
    intent = Column(JSON)
    workflow = Column(JSON)

    agents = association_proxy('bot_agents', 'agent')
    actions = association_proxy('bot_actions', 'action')
    botTests = relationship('TestBot', viewonly=True)

    errors = ''

    def __init__(self, name='', description='', enabled=True, searchable=True, intent={}, workflow={}, params={}, **kwargs):
        self.name = name
        self.description = description
        self.enabled = enabled
        self.searchable = searchable
        self.intent = intent
        self.workflow = workflow
        VersionedMixin.__init__(self, name=name)
        if params:
            self.params = params
        else:
            ParametrizedMixin.__init__(self, kwargs)

    def __repr__(self):
        return 'Bot({})'.format(self.id)

    def __str__(self):
        d = self.__dict__
        for key, value in self.__dict__:
            if not self.is_json(value):
                d.pop(key)

        return str(d)

    def is_json(self, obj):
        try:
            json.dump(obj)
            return True
        except Exception:
            return False

    def clone(self, agent=None):
        db.session.expunge(self)
        make_transient(self)

        prefix = 'clone.' if agent else ''
        self.name = prefix + self.name
        if agent:
            self.agents.append(agent)
        self.id = None

        db.session.add(self)
        db.session.commit()

    def validate(mapper, connect, self):
        errors = {}

        if not self.name or len(self.name) < 2:
            errors['name'] = 'name must not be empty'

        if not self.description or len(self.description) < 2:
            errors['description'] = 'Please provide a good description'

        if self.searchable and not self.intent.get('positives'):
            errors['intent'] = 'Please provide at least one positive intent. '

        if len(self.params.get('answer_not_related', '')) < 2:
            errors['answer_not_related'] = 'Please provide a good answer for not related, for out of topic queries. '

        if len(self.params.get('answer_error', '')) < 2:
            errors['answer_error'] = 'Please provide a good answer for error case, for bot connection issues.'

        if errors != {}:
            exception = ValueError()
            exception.errors = errors
            raise exception


class TestBot(db.Model, VersionedMixin, AuditMixin):
    __tablename__ = 'bot_testing'

    id = Column(Integer, ForeignKey('bot.id'), primary_key=True)
    name = Column(String(128))
    test_set = Column(JSON)
    test_passed = Column(Boolean)

    def __repr__(self):
        return 'TestBot({}, {}, {})'.format(self.id, self.name, self.test_set)


listen(Bot, 'before_insert', Bot.validate)
listen(Bot, 'before_update', Bot.validate)


