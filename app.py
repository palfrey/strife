from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import oauthlib
from dotenv import load_dotenv
from .models import make_models
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
client_id = os.getenv("DISCORD_CLIENT_ID")
client_secret = os.getenv("DISCORD_CLIENT_SECRET")
app.secret_key = os.getenv("SECRET_KEY")

authorization_base_url = 'https://discordapp.com/api/oauth2/authorize'
token_url = 'https://discordapp.com/api/oauth2/token'

@app.before_request
def make_session_permanent():
    session.permanent = True

db = SQLAlchemy(app)
models = make_models(db)
User = models['User']
Connection = models['Connection']
migrate = Migrate(app, db)

scopes = ['identify', 'connections']

@app.route("/")
def index():
    user_id = session.get('user', None)
    user = User.query.get(user_id) if user_id != None else None
    return render_template('index.html', user_id=user_id, user=user)

@app.route("/profile/<id>")
def profile(id):
    user = User.query.get_or_404(id)
    user_id = session.get('user', None)
    if user_id == user.id:
        discord = OAuth2Session(client_id, token=session['oauth_token'])
        connections = discord.get('https://discordapp.com/api/users/@me/connections').json()
        current_connections = dict([((c['type'], c['id']), c) for c in connections])
        stored_connections = dict([((c.kind, c.discord_id), c) for c in user.connections])
        found_connections = []
        for conn_key in current_connections.keys():
            conn = current_connections[conn_key]
            if conn['visibility'] == 0:
                continue
            if conn_key in stored_connections:
                found_connections.append(stored_connections[conn_key])
                del stored_connections[conn_key]
            else:
                new_conn = Connection(user_id=user.id, discord_id=conn['id'], name=conn['name'], kind=conn['type'])
                db.session.add(new_conn)
        for c in stored_connections.values():
            db.session.delete(c)
        db.session.commit()
    return render_template('profile.html', user=user, user_id=user_id, connections=sorted(user.connections, key=lambda c: c.kind), url=request.url)

@app.route("/login")
def login():
    discord = OAuth2Session(client_id, scope=scopes)
    authorization_url, state = discord.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    discord = OAuth2Session(client_id, state=session['oauth_state'])
    try:
        token = discord.fetch_token(token_url, client_secret=client_secret,
                                authorization_response=request.url)
    except oauthlib.oauth2.rfc6749.errors.InvalidClientIdError:
        # got re-used, so retry
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