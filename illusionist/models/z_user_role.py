from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from illusionist.models.user import User
from illusionist.models.role import Role
from python_utils.flask_sqlalchemy_base import db, AuditMixin


# class UserRole(db.Model, AuditMixin):
#     __tablename__ = 'user_role'
#
#     user_id = Column(Integer, ForeignKey(Role.id), primary_key=True)
#     role_id = Column(Integer, ForeignKey(User.id), primary_key=True)
#     created_on = Column(DateTime)
#     changed_on = Column(DateTime)
#     user = relationship('User', backref=backref('user_roles', cascade="all, delete-orphan"))
#     role = relationship('Role', backref=backref('role_users', cascade="all, delete-orphan"))
#
#     def __init__(self, user, role):
#         if isinstance(user, User):
#             self.user = user
#         if isinstance(role, Role):
#             self.role = role
