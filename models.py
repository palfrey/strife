from .guid import GUID
from .json_field import JSONEncodedDict
import uuid

def make_models(db):
    class User(db.Model):
        id = db.Column(GUID, primary_key=True, default=uuid.uuid4())
        discord_id = db.Column(db.String(80), unique=True, nullable=False)
        username = db.Column(db.String(80), nullable=False)
        discriminator = db.Column(db.String(4), nullable=False)
        avatar_hash = db.Column(db.String(120))
        oauth_token = db.Column(JSONEncodedDict)

        def __repr__(self):
            return '<User %r>' % self.username
    
    return {"User": User}