import os
import getpass
import json
import yaml
import python_utils.vault


def get_config(config_type, config_ext, config_mod):
    u = 'local_' + getpass.getuser()
    user_config_file = find_config_file(config_type, config_ext, u)
    if os.path.isfile(user_config_file):
        config_file = user_config_file
    elif 'CONFIG_ENV' in os.environ:
        env = os.environ['CONFIG_ENV']
        config_file = find_config_file(config_type, config_ext, env)
    else:
        config_file = "/etc/{type}_dev.{ext}".format(type=config_type, ext=config_ext)

    return load_config(config_file, config_mod)


def find_config_file(config_type, config_ext, env):
    config_file = "{basedir}/../../configs/{type}_{env}.{ext}".format(
        basedir=os.path.dirname(os.path.realpath(__file__)),
        type=config_type, env=env, ext=config_ext)
    return config_file


def load_config(config_file, config_mod):
    if not os.path.isfile(config_file):
        print('Config file missing, {}. Make sure CONFIG_ENV is set correctly.'.format(config_file))
    else:
        with open(config_file) as data:
            if config_mod.__name__ == 'yaml':
                return config_mod.load(data, Loader=yaml.FullLoader)
            else:
                return config_mod.load(data)
    print("Read config file {}.".format(config_file))


def inject_to_config_dict(s_config, path, value):
    parts = path.split('/')
    if 'CONFIG_ENV' in os.environ:
        env = os.environ['CONFIG_ENV']
    val = value
    for key in reversed(parts):
        if key == env:
            continue
        val = {key: val}
    update_dict(s_config, val)


def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def load_config_from_vault(s_config):
    """ Vault Address and Token should be provided to extract other keys.
        This method will read only service level configuration. server-*.yml should be configured with following
        template structure.
        vault:
          addr: "http://localhost:8200/"
          service:
            token: "XXXXXXX-0b46-a7e0-XXXX-XXXXXXXXX"
            mount: "astound"
            paths:
                - "/dev/mysql/illusionist"
    """
    if validate_vault_config(s_config):
        vault_addr = s_config['vault'].get('addr', '')
        vault_service = s_config['vault'].get('service', {})

        vault_token = os.environ.get('VAULT_TOKEN', vault_service.get('token', ''))
        mount = vault_service.get('mount', '')
        paths = vault_service.get('paths', '')

        if vault_addr and vault_token:
            vault = python_utils.vault.Vault(vault_addr, vault_token)
            for path in paths:
                value = vault.get_value(mount, path)
                inject_to_config_dict(s_config, path, value)
        else:
            print("No Vault Address and Token Specified.")

    return s_config


def validate_vault_config(s_config):
    if not s_config:
        return False

    if 'vault' in s_config.keys():
        return True
    return False


logging_config = get_config('logging', 'json', json)
server_config = get_config('server', 'yml', yaml)

server_config = load_config_from_vault(server_config)

# deprecating
app_config = server_config


