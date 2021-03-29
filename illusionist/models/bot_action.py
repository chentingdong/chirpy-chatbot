from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, ForeignKey
from illusionist.models.bot import Bot
from illusionist.models.action import Action
from python_utils.flask_sqlalchemy_base import db, AuditMixin, JsonDeSerMixin
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BotAction(db.Model, AuditMixin, JsonDeSerMixin):
    __tablename__ = 'bot_action'

    bot_id = Column(Integer, ForeignKey(Bot.id), primary_key=True)
    action_id = Column(Integer, ForeignKey(Action.id), primary_key=True)

    bot = relationship('Bot', backref=backref('bot_actions', cascade="all, delete-orphan"))
    action = relationship('Action', backref=backref('action_bots', cascade="all, delete-orphan"))

    def __init__(self, child):
        if isinstance(child, Bot):
            self.bot = child
        if isinstance(child, Action):
            self.action = child
