import sys
from hvac import Client, exceptions


class AuthenticationFailure(Exception):
    pass


class OperationNotAllowed(Exception):
    pass


class AddressNotFound(Exception):
    pass


class TokenNotFound(Exception):
    pass


class PathNotSpecified(Exception):
    pass


class Vault:

    def __init__(self, vault_addr: str, vault_token: str):
        """
        Initialize the Vault class. Token is inject via standard config followed as of now.

        :param vault_addr:
        :param vault_token:
        """
        if not vault_addr:
            raise AddressNotFound("Vault Address needs to be specified.")
        self.vault_addr = vault_addr

        if not vault_token:
            raise TokenNotFound("Vault Token should be specified.")
        self.vault_token = vault_token

        # TODO: Extend later to include TLS with client-side certificate authentication
        self.vault_client = Client(url=self.vault_addr, token=self.vault_token)

        if not self.vault_client.is_authenticated():
            error_msg = 'Unable to authenticate to the Vault service using token.'
            raise AuthenticationFailure(error_msg)

    def get_value(self, mount, path):
        """
        Returns the configuration value corresponding to the path. Based on the key this can be a singular-value
        or multi-valued object.

        :param mount: Specify the engine name as mount point 'e.g. astound'
        :param path: path to config that needs to be fetched
        :return: Dict of results corresponding to the key
        """

        if not path:
            raise PathNotSpecified("Path to read the secret should be specified.")

        try:
            result = self.vault_client.secrets.kv.v2.read_secret_version(path=path, mount_point=mount)

            # TODO: More exceptions can be caught
        except exceptions.Forbidden:
            error_msg = "Access denied, invalid token corresponding to policy."
            tb = sys.exc_info()[2]
            raise OperationNotAllowed(error_msg).with_traceback(tb)

        return result['data']['data']

    # def put_value(self, mount, path, secret):
    #     """
    #     Write a secret to the Vault. Please use ONLY authorized path to the Vault to write the data.
    #     If you get UnAuthorized exception then try to look into the path.
    #
    #     :param mount: Mount point or secret engine name e.g. 'astound'
    #     :param path: path to store the KV secret which is presented as dict
    #     :param secret: secrets as dict
    #     :return: None
    #     """
    #
    #     if not path:
    #         raise PathNotSpecified("Path to write the secret should be specified.")
    #
    #     try:
    #         self.vault_client.secrets.kv.v2.create_or_update_secret(mount_point=mount, path=path, secret=secret)
    #     except (exceptions.Forbidden, exceptions.Unauthorized):
    #         error_msg = "Unable to write the secret to vault."
    #         tb = sys.exc_info()[2]
    #         raise OperationNotAllowed(error_msg).with_traceback(tb)
    #
    # def remove_value(self, mount, path):
    #     """
    #     Deletes a key path from the Vault. Please note policy corresponding to the token will be enforced, and if
    #     the delete privileges are not there for a given path, exception will be thrown.
    #
    #     :param mount: Mount point or secret engine name e.g. 'astound'
    #     :param path: path to store the KV secret which is presented as dict
    #     :return:
    #     """
    #
    #     if not path:
    #         raise PathNotSpecified("Path to delete the secret should be specified.")
    #
    #     try:
    #         self.vault_client.secrets.kv.v1.delete_secret(mount_point=mount, path=path)
    #     except (exceptions.Forbidden, exceptions.Unauthorized):
    #         error_msg = "Unable to write the secret to vault."
    #         tb = sys.exc_info()[2]
    #         raise OperationNotAllowed(error_msg).with_traceback(tb)

