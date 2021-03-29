from python_utils.flask_sqlalchemy_base import db, AuditMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from illusionist.models.role import Role
import json


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), index=True)
    password = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile = Column(JSON)
    created_on = Column(DateTime)
    changed_on = Column(DateTime)

    def __init__(self, id=None, username=None, password=None, first_name=None, last_name=None):
        if id:
            self.id = id
        if username:
            self.username = username
        if password:
            self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return json.dumps(self.get_info())

    def get_info(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'roles': [ur.role.name for ur in self.user_role],
            'profile': self.profile
        }


class UserRole(db.Model, AuditMixin):
    __tablename__ = 'user_role'

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    role_id = Column(Integer, ForeignKey(Role.id), primary_key=True)
    created_on = Column(DateTime)
    changed_on = Column(DateTime)
    user = relationship('User', backref=backref('user_role', cascade="all, delete-orphan"))
    role = relationship('Role', backref=backref('role_user', cascade="all, delete-orphan"))

    def __init__(self, user, role):
        if isinstance(user, User):
            self.user = user
        if isinstance(role, Role):
            self.role = role
