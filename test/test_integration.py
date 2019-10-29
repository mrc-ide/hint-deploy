import io
import pytest
import requests
import time

from contextlib import redirect_stdout

import constellation.docker_util as docker_util

from src import hint_cli, hint_deploy


def test_start_hint():
    cfg = hint_deploy.HintConfig("config")
    obj = hint_deploy.hint_constellation(cfg)
    obj.status()
    obj.start()

    res = requests.get("http://localhost:8080")

    assert res.status_code == 200
    assert "Login" in res.content.decode("UTF-8")

    assert docker_util.network_exists("hint_nw")
    assert docker_util.volume_exists("hint_db_data")
    assert docker_util.volume_exists("hint_uploads")
    assert docker_util.container_exists("hint_db")
    assert docker_util.container_exists("hint_redis")
    assert docker_util.container_exists("hint_hintr")
    assert docker_util.container_exists("hint_hint")

    # Some basic user management
    user = "test@example.com"
    f = io.StringIO()
    with redirect_stdout(f):
        hint_deploy.hint_user(cfg, "add-user", user, True, "password")

    p = f.getvalue()
    assert "Adding user {}".format(user) in p
    assert p.strip().split("\n")[-1] == "OK"

    f = io.StringIO()
    with redirect_stdout(f):
        hint_deploy.hint_user(cfg, "user-exists", user, False)

    assert f.getvalue() == "Checking if user exists: {}\ntrue\n".format(user)

    f = io.StringIO()
    with redirect_stdout(f):
        hint_deploy.hint_user(cfg, "remove-user", user, False)

    assert f.getvalue() == "Removing user {}\nOK\n".format(user)

    obj.destroy()

    assert not docker_util.network_exists("hint_nw")
    assert not docker_util.volume_exists("hint_db_data")
    assert not docker_util.volume_exists("hint_uploads")
    assert not docker_util.container_exists("hint_db")
    assert not docker_util.container_exists("hint_redis")
    assert not docker_util.container_exists("hint_hintr")
    assert not docker_util.container_exists("hint_hint")


def test_start_hint_from_cli():
    hint_cli.main(["start"])
    res = requests.get("http://localhost:8080")
    assert res.status_code == 200
    assert "Login" in res.content.decode("UTF-8")
    hint_cli.main(["stop"])
