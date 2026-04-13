from Logic.security import validateCSRF

from flask import Flask, session


def test_csrf_valid():
    app = Flask(__name__)

    app.secret_key = "test"

    with app.test_request_context("/", method="POST", data={"csrfToken": "abc"}):
        session["csrfToken"] = "abc"

        assert validateCSRF() is True


def test_csrf_invalid():
    app = Flask(__name__)

    app.secret_key = "test"

    with app.test_request_context("/", method="POST", data={"csrfToken": "wrong"}):
        session["csrfToken"] = "abc"

        assert validateCSRF() is False


def test_csrf_missing():
    app = Flask(__name__)

    app.secret_key = "test"

    with app.test_request_context("/", method="POST", data={}):
        session["csrfToken"] = "abc"

        assert validateCSRF() is False
