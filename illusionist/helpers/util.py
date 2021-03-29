# all functions are exported. do not add global variables.
import datetime
import enum
import re
import uuid
import math

from attr import attr

from python_utils.logger import logger_console

NAMESPACE_ILLUSIONIST = uuid.UUID('6cd5e5af-598d-4c0d-ac10-71988c0e4af6')


class Utils:
    @staticmethod
    def round(f, digits):
        n = 10 ** digits
        return math.ceil(f * n) / n

    @staticmethod
    def keys_exists(element, *keys):
        """
        Check if *keys (nested) exists in `element` (dict).
        :param element:
        :param keys:
        :return:
        """
        try:
            d = dict(element)
            logger_console.error(AttributeError('keys_exists() expects dict as first argument.'))
        except Exception:
            return False

        if type(d) is not dict:
            logger_console.error(AttributeError('keys_exists() expects dict as first argument.'))
            return False

        if len(keys) == 0:
            logger_console.error(AttributeError('keys_exists() expects at least two arguments, one given.'))
            return False

        for key in keys:
            try:
                d = d[key]
            except KeyError:
                return False
        return True

    @staticmethod
    def clean_string(s):
        return re.sub('[^0-9a-zA-Z ]+', '', s)

    @staticmethod
    def serialize(val):
        if isinstance(val, datetime):
            return val.isoformat() + "Z"
        elif isinstance(val, enum.Enum):
            return val.value
        elif attr.has(val.__class__):
            return attr.asdict(val)
        elif isinstance(val, Exception):
            return {
                "error": val.__class__.__name__,
                "args": val.args,
            }
        return str(val)


def get_app():
    from flask import current_app
    if current_app:
        return current_app
    else:
        from illusionist.app import create_app
        return create_app()