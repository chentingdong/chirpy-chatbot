from python_utils.flask_sqlalchemy_base import db


class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))
    content = db.Column(db.Text)
    version = db.Column(db.Integer)
    db.UniqueConstraint('name', 'version')

    def __init__(self, name, content, version=1):
        self.name = name
        self.content = content
        self.version = version

    def __repr__(self):
        return '<Template %r>' % self.name

    def to_json(self):
        result = {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'content': self.content
        }
        return result

