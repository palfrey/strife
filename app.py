from requests_oauthlib import OAuth2Session

from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify

client_id = "608731377990500370"
client_secret = "t7faFXVZFLLkvZe0GsR8iHxaEd3qdXip"
authorization_base_url = 'https://discordapp.com/api/oauth2/authorize'
token_url = 'https://discordapp.com/api/oauth2/token'

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
scopes = ['identify', 'connections']

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
    token = discord.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    return jsonify(discord.get('https://discordapp.com/api/users/@me').json())