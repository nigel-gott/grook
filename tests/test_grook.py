import pytest
from flask import url_for


def test_app(client):
    assert client.get(url_for('hello')).status_code == 200
