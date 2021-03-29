from python_utils.flask_sqlalchemy_base import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime
import json


class Role(db.Model):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    created_on = Column(DateTime)
    changed_on = Column(DateTime)

    def __init__(self, id=None, name=None):
        if id:
            self.id = id
        if name:
            self.name = name

    def __repr__(self):
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'created_on': self.created_on,
            'changed_on': self.changed_on
        })