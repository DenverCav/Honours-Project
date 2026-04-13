def test_home(client):
    response = client.get("/")

    assert response.status_code == 200


def test_leaderboard(client):
    response = client.get("/leaderboard")

    assert response.status_code == 200


def test_profile_redirect(client):
    response = client.get("/profile")

    assert response.status_code == 302


def test_submit_score_redirect(client):
    response = client.get("/submitScore")

    assert response.status_code == 302


def test_demo_route(client):
    response = client.get("/demo")

    assert response.status_code == 302
