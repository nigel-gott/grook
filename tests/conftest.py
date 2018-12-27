import boto3
import pytest
from moto import mock_dynamodb2

from grook.server import create_app

@pytest.yield_fixture()
def dynamodb():
    mock_dynamodb2().start()

    client = boto3.client("dynamodb")
    resource = boto3.resource("dynamodb")

    yield client, resource

    mock_dynamodb2().stop()

@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    return app

