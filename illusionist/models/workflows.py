from python_utils.flask_sqlalchemy_base import db


class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))
    content = db.Column(db.Text)
    version = db.Column(db.Integer)
    release = db.Column(db.String(255))
    tag = db.Column(db.String(255))
    db.UniqueConstraint('name', 'version')

    def __init__(self, name, content, version, release, created_at, tag=None):
      self.name = name
      self.content = content
      self.version = version
      self.release = release
      self.created_at = created_at
      self.tag = tag

    def __repr__(self):
        return '<Workflow %r, version %r>' % (self.name, self.version)

    def to_json(self, with_content: bool = True):
      result = {
        'id': self.id,
        'name': self.name,
        'version': self.version,
        'release': self.release,
        'tag': self.tag,
        'created_at': self.created_at
      }
      if with_content:
        result['content'] = self.content

      return result
