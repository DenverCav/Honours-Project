import pytest

from main import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update({

        "TESTING": True,

        "SECRET_KEY": "3721f426bd596075e77c4bc6de53c18afface96aefc4bba88333bd7fb3c2d9af"

    })

    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
