from collections import OrderedDict

import uuid
import json
from jsonschema import validate
import os
import subprocess


def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


def hash_uuid(name_to_hash, project):
    namespace = uuid.uuid5(uuid.NAMESPACE_X500, project)
    return str(uuid.uuid5(namespace, name_to_hash))


def validate_json(json_string, schema=None):
    try:
        json_object = json.loads(json_string)
        if schema:
            validate(json_object, schema)
        return {'success': True, 'reason': ''}
    except ValueError as e:
        return {'success': False, 'reason': str(e)}


def order_dict(d, keys):
    selected = {key: d[key] for key in keys}
    ordered = OrderedDict(sorted(selected.items(), key=lambda t: keys.index(t[0])))
    return ordered


def get_version():
    if 'LUKE_IMAGE_TAG' in os.environ:
        release_version = str(os.environ['LUKE_IMAGE_TAG'])
    elif 'GIT_COMMIT' in os.environ:
        release_version = str(os.environ['GIT_COMMIT'])
    elif 'ASTOUND_RELEASE_VERSION' in os.environ:
        release_version = str(os.environ['ASTOUND_RELEASE_VERSION'])
    else:
        try:
            release_version = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD']).decode("utf-8")
        except:
            if 'USER' in os.environ:
                release_version = str(os.environ['USER'])
            else:
                release_version = 'NotFound'

    release_version = release_version.rstrip()

    return release_version

def is_json(json_str):
    try:
        json_object = json.loads(json_str)
    except ValueError as e:
        return False
    return True


version = get_version()
