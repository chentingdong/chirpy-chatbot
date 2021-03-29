import pytest
from python_utils.logger import logger
from flask import Flask, jsonify
from illusionist.response import Response
from python_utils.vault import Vault

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    app.config['SERVER_NAME'] = 'localhost'

    @app.route('/health-check', methods=['GET'])
    @logger.api_access()
    def health_check():
        return 'OK'

    @app.route('/api_200', methods=['POST'])
    @logger.api_access()
    def api_200():
        response = Response()
        response.add_payload('test', {
            'key': 'value',
            'key2': 'value2'
        })
        response.session_id = 'test'
        response.success()
        return jsonify(**response.object)

    @app.route('/api_401', methods=['POST'])
    @logger.api_access()
    def api_401():
        response = Response()
        return jsonify(**response.object)

    app.app_context().push()
    return app


@pytest.fixture
def conversation():
    req = {
        "org_id": "1",
        "user_id": "1",
        "workflow": "albertsons_updated",
        "utterance": {
            "utterance": "When will i get my tax form in the mail?"
        }
    }
    return req


class VaultClient(object):

    def __init__(self, addr="http://localhost:8200", token="5b357544-0b46-a7e0-ab94-ff39a12aaabd"):
        self.addr = addr
        self.token = token

    def get_client(self):
        return Vault(self.addr, self.token)


@pytest.fixture
def client():
    return VaultClient().get_client()


@pytest.fixture
def client2(token="b573cb89-b803-33e6-e792-8acf1e297dfe"):
    return VaultClient(token=token).get_client()
