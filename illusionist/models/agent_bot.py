from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, ForeignKey
from illusionist.models.agent import Agent
from illusionist.models.bot import Bot
from python_utils.flask_sqlalchemy_base import db, AuditMixin, JsonDeSerMixin
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AgentBot(db.Model, AuditMixin, JsonDeSerMixin):
    __tablename__ = 'agent_bot'

    agent_id = Column(Integer, ForeignKey(Agent.id), primary_key=True)
    bot_id = Column(Integer, ForeignKey(Bot.id), primary_key=True)

    agent = relationship('Agent', backref=backref('agent_bots', cascade="all, delete-orphan"))
    bot = relationship('Bot', backref=backref('bot_agents', cascade="all, delete-orphan"))

    def __init__(self, child):
        if isinstance(child, Agent):
            self.agent = child
        if isinstance(child, Bot):
            self.bot = child
