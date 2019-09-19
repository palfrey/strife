import tempfile
import pytest
from flask_migrate import upgrade
import uuid
import httpretty

import os
import sys
sys.path.append(os.getcwd())

from app import app, models, db

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///%s" % db_path
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            upgrade()
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def test_index(client):
    rv = client.get('/')
    assert b'Get your profile' in rv.data

@httpretty.activate
def test_profile(client):
    user = models['User']()
    user.discord_id = 'foo'
    user.username = 'bar'
    user.discriminator = 'baz'
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = user.id
        sess['oauth_token'] = {"access_token":'DUMMY_TOKEN'}

    httpretty.register_uri(httpretty.GET, "https://discordapp.com/api/users/@me/connections",
                            body="[]")
    
    rv = client.get("/profile/%s" % user.id)
    assert b'No connections to other sites' in rv.data
    assert b'bar#baz' in rv.data