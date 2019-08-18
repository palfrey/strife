from .guid import GUID
from .json_field import JSONEncodedDict
import uuid
from titlecase import titlecase

def make_models(db):
    class User(db.Model):
        id = db.Column(GUID, primary_key=True, default=uuid.uuid4())
        discord_id = db.Column(db.String(80), unique=True, nullable=False)
        username = db.Column(db.String(80), nullable=False)
        discriminator = db.Column(db.String(4), nullable=False)
        avatar_hash = db.Column(db.String(120))
        oauth_token = db.Column(JSONEncodedDict)
        connections = db.relationship('Connection', backref='user', lazy=True)

        def __repr__(self):
            return '<User %r>' % self.username

    class Connection(db.Model):
        id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
        user_id = db.Column(GUID, db.ForeignKey('user.id'), nullable=False)
        discord_id = db.Column(db.String(80), unique=True, nullable=False)
        name = db.Column(db.String(80), nullable=False)
        kind = db.Column(db.String(80), nullable=False)

        def display_name(self):
            return titlecase(self.kind)

        def link(self):
            if self.kind == "steam":
                return "https://steamcommunity.com/profiles/%s" % self.discord_id
            elif self.kind == "twitch":
                return "https://www.twitch.tv/%s" % self.name
            elif self.kind == "twitter":
                return "https://twitter.com/%s" % self.name
            elif self.kind == "xbox":
                return "http://live.xbox.com/Profile?Gamertag=%s" % self.name
            elif self.kind == "skype":
                return "skype:%s" % self.name
            elif self.kind == "facebook":
                #raise Exception(self.__dict__)
                return "https://www.facebook.com/search/top/?q=%s&epa=SEARCH_BOX" % self.name
            else:
                return ""

    return {"User": User, "Connection": Connection}