# TODO: Remove live Vault dependency generally not a good idea. Need to remove the dependency on hard-coded keys
#  and paths if possible.

import pytest
from python_utils.vault import Vault, AddressNotFound, TokenNotFound, OperationNotAllowed


def test_client_no_value(client):
    with pytest.raises(OperationNotAllowed):
        client.get_value('secrets', '/')


@pytest.mark.parametrize('path', (
        '/dev',
        '/dev/titan',
        '/dev/luke'
))
def test_client_forbidden(client, path):
    with pytest.raises(OperationNotAllowed):
        client.get_value('secret', path)


def test_client_returns_system_config(client):
    result = client.get_value('astound', '/dev/titan')
    assert isinstance(result, dict), "Expected dictionary."
    assert result['data']['db_host'] is not None, "Expected db_host key."
    assert result['data']['db_password'] is not None, "Expected db_password key."
    assert result['data']['sqlalchemy_database_uri'] is not None, "Expected sqlalchemy_database_uri key."


@pytest.mark.parametrize(('vault_addr', 'vault_token'), (
        ('', ''),
        ('', 'SOME_TOKEN'),
))
def test_client_init_empty_params(vault_addr, vault_token):
    with pytest.raises(AddressNotFound):
        Vault(vault_addr, vault_token)


@pytest.mark.parametrize(('vault_addr', 'vault_token'), (
        ('http://localhost:8200/', ''),
        ('SOME_ADDRESS', ''),
))
def test_client_init(vault_addr, vault_token):
    with pytest.raises(TokenNotFound):
        Vault(vault_addr, vault_token)


def test_client_returns_forbidden_application_config(client):
    with pytest.raises(OperationNotAllowed):
        client.get_value('astound', 'dev/customertokens/adidas')


def test_client_returns_application_config(client2):
    result = client2.get_value('astound', '/dev/customertokens/adidas')
    assert isinstance(result, dict), "Expected dictionary."
    assert result['data']['servicenow'] is not None, "Expected servicenow key under adidas path."


def test_client_put_secret(client2):
    secret = dict(servicenow='agile_service_now_secret')
    client2.put_value('astound', 'dev/customertokens/agile/', secret)
    result = client2.get_value('astound', 'dev/customertokens/agile/')
    assert result['data']['servicenow'] == secret['servicenow'], "Key Not updated."


def test_client_put_secret_update_with_new(client2):
    secret = dict(servicenow='agile_service_now_secret_updated', slack='some_slack_token')
    client2.put_value('astound', 'dev/customertokens/agile/', secret)
    result = client2.get_value('astound', 'dev/customertokens/agile/')
    assert result['data']['servicenow'] == secret['servicenow'], "Key Not updated."


def test_client_deletion_should_not_be_allowed(client2):
    with pytest.raises(OperationNotAllowed):
        client2.remove_value('astound', 'dev/customertokens/agile/')

