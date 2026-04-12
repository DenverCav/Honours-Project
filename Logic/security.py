from urllib.parse import urlparse
from flask import session, request


def validateCSRF():
    token = request.form.get("csrfToken")
    return bool (token and token == session.get("csrfToken"))

def isValidUrl(url):
    try:
        result = urlparse(url)
        return result.scheme in ["http", "https"]
    except:
        return False