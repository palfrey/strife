from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import oauthlib

from .models import make_models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.before_request
def make_session_permanent():
    session.permanent = True

db = SQLAlchemy(app)
models = make_models(db)
User = models['User']
migrate = Migrate(app, db)

client_id = "608731377990500370"
client_secret = "t7faFXVZFLLkvZe0GsR8iHxaEd3qdXip"
authorization_base_url = 'https://discordapp.com/api/oauth2/authorize'
token_url = 'https://discordapp.com/api/oauth2/token'

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
scopes = ['identify', 'connections']

@app.route("/")
def index():
    return render_template('index.html', user_id=session.get('user', None))

@app.route("/profile/<id>")
def profile(id):
    return render_template('profile.html', user=User.query.get(id), user_id=session.get('user', None))
    #     discord = OAuth2Session(client_id, token=session['oauth_token'])
    #     discord_user = discord.get('https://discordapp.com/api/users/@me').json()
    #     return str(session['user'])

@app.route("/login")
def login():
    discord = OAuth2Session(client_id, scope=scopes)
    authorization_url, state = discord.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    discord = OAuth2Session(client_id, state=session['oauth_state'])
    try:
        token = discord.fetch_token(token_url, client_secret=client_secret,
                                authorization_response=request.url)
    except oauthlib.oauth2.rfc6749.errors.InvalidClientIdError:
        # got refreshed
        return redirect("/login")
    discord_user = discord.get('https://discordapp.com/api/users/@me').json()
    discord_id = discord_user['id']
    user = User.query.filter_by(discord_id=discord_id).first()
    if user == None:
        user = User()
        db.session.add(user)
    user.discord_id = discord_id
    user.username = discord_user['username']
    user.discriminator = discord_user['discriminator']
    user.avatar_hash = discord_user['avatar']
    user.oauth_token=token
    db.session.commit()
    session['user'] = user.id
    session['oauth_token'] = token
    return redirect("/profile/%s" % str(user.id))