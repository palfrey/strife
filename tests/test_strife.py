import tempfile
import pytest
from flask_migrate import upgrade
import uuid

import os
import sys
sys.path.append(os.getcwd())

from app import app, models, db

@pytest.fixture
def client():
    db_fd, app.config['DATABASE_URL'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            upgrade()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE_URL'])

def test_index(client):
    rv = client.get('/')
    assert b'Get your profile' in rv.data

def test_profile(client):
    test_uuid = uuid.uuid4()
    user = models['User']()
    db.session.add(user)
    db.session.commit()

    rv = client.get("/profile/%s" % test_uuid)
    assert b'Get your profile' in rv.data