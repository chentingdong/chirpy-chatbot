import json
import logging
from collections import OrderedDict
from datetime import datetime
import uuid
import re

logger = logging.getLogger(__name__)

TIME_ORIGIN = datetime(1900, 1, 1, 0, 0, 0, 0).isoformat()

FIELD_TYPES = [
    'UID',
    'Phrase',
    'Sentence',
    'Text',
    'Integer',
    'Real',
    'DateTime',
    'Zipcode',
    'Tensor',
    'Other'
]


# TODO make this part of ColumnType
def match(value, ctype):
    if ctype == 'Other':
        return True
    elif ctype in ['Phrase', 'Sentence', 'Text', 'UID']:
        if isinstance(value, str):
            return True
    elif ctype == 'Integer':
        if isinstance(value, int):
            return True
    elif ctype == 'Real':
        if isinstance(value, float):
            return True
    elif ctype == 'DateTime':
        if isinstance(value, str):
            try:
                datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                return True
            except:
                pass
    elif ctype == 'Zipcode':
        if isinstance(value, str) and re.search('(^\d{5}$)|(^\d{5}-\d{4}$)', value):
            return True

    msg = 'Schema check failed for {} against {}'.format(value, ctype)
    logger.error(msg)
    raise ValueError(msg)


# TODO make this part of ColumnType
def default(ctype):
    if ctype == 'UID':
        return str(uuid.uuid4())
    elif ctype == 'Integer':
        return 0
    elif ctype == 'Real':
        return 0.0
    elif ctype == 'DateTime':
        return TIME_ORIGIN
    elif ctype == 'Zipcode':
        return '94025'
    else:
        return ''


class Schema:
    """
    Schema provides a dynamic schema declaration
    Example:
        <pre>
        Schema(name='incident')

        [
            {'name': 'short_description', 'type': 'Sentence', 'default': ''},
            {'name': 'created_on', 'type': 'DateTime', 'default': TIME_ORIGIN}
        ]
        </pre>
    """
    def __init__(self, name='', names=None, types=None, defaults=None, primary=None):
        """
        :param name: name of the Schema
        :type name: str
        :param names: name for each field, order matters
        :type names: List[str]
        :param types: type for each field
        :type types: Dict
        :param defaults: default value for each field
        :type defaults: Dict
        :param primary: primary field name
        :type primary: str
        """
        self.name = name
        if names is None:
            names = []
        if types is None:
            types = {}
        if defaults is None:
            defaults = {}
        self._names = names
        self._types = types
        self._defaults = defaults
        self.primary = primary
        if primary is None and len(names) > 0:
            self.primary = names[0]

        for name in names:
            if name not in types:
                msg = '{} does not exist in the types'.format(name)
                logger.error(msg)
                raise ValueError(msg)
            if name not in defaults:
                defaults[name] = default(types[name])
            elif not match(defaults[name], types[name]):
                msg = '{} does not match type {} for {}'.format(defaults[name], types[name], name)
                logger.error(msg)
                raise ValueError(msg)

    def add(self, field_name, field_type='Text', field_default=default('Text')):
        if field_name not in self._types:
            self._names.append(field_name)
            self._types[field_name] = field_type
            self._defaults[field_name] = field_default
            if self.primary is None:
                self.primary = field_name
        elif self._types.get(field_name) != field_type:
            msg = 'Field {}:{}:{} already exists in this Schema'.format(field_name,
                                                                        self._types.get(field_name),
                                                                        field_default)
            logger.error(msg)
            raise ValueError(msg)

    def remove(self, field_name):
        if field_name in self._types:
            self._names.remove(field_name)
            self._types.pop(field_name)
            self._defaults.pop(field_name)
            if self.primary == field_name:
                if len(self._defaults) > 0:
                    self.primary = self._names[0]
                else:
                    self.primary = None

    def update(self, field_name, field_type='Text', field_default=default('Text')):
        if field_name not in self._types:
            self._names.append(field_name)
            self._types[field_name] = field_type
            self._defaults[field_name] = field_default
        elif self._types.get(field_name) != field_type:
            self._types[field_name] = field_type
            self._defaults[field_name] = field_default

    @property
    def json(self):
        return json.dumps({'name': self.name, 'schema': self.schema, 'primary': self.primary})

    @json.setter
    def json(self, json_str):
        j = json.loads(json_str)
        self.name = j.get('name', '')
        self.primary = j.get('primary')
        schema = j.get('schema', [])
        if not isinstance(schema, list):
            msg = 'schema should be a list of dictionary instead of {}'.format(json.dumps(schema))
            logger.error(msg)
            raise ValueError(msg)
        for item in schema:
            name = item.get('name')
            if not name:
                msg = 'schema field can not have emtpy name : {}'.format(json.dumps(schema))
                logger.error(msg)
                raise ValueError(msg)
            t = item.get('type')
            if not t:
                msg = 'schema field can not have empty type : {}'.format(json.dumps(schema))
                logger.error(msg)
                raise ValueError(msg)
            d = item.get('default', default(t))
            self._names.append(item.get('name'))
            self._types[name] = t
            self._defaults[name] = d

    def default(self, key):
        return self._defaults.get(key, None)

    @property
    def schema(self):
        return [{'name': name, 'type': self._types[name], 'default': self._defaults[name]} for name in self._names]

    @property
    def keys(self):
        return self._names

    def check(self, values):
        """
        Check the values against this schema
        :param values:dictionary of name and values
        :return: True if it passes the schema definition, ValueError is raised otherwise
        """
        for key, value in values.items():
            if key not in self._types:
                msg = 'field {} does not exist in the schema {}'.format(key, self.json)
                logger.error(msg)
                raise ValueError(msg)
            match(value, self._types[key])
        return True

    def entity(self, values=None, check=False):
        """
        Create an entity out of the given values. If fields missing, defaults will be provided. If check is True,
        the values will be checked against this Schema
        :param values: values used to create the entity, if not a dictionary, it is assumed to be a primary value.
        :param check: whether to check the schema or not
        :return: Entity
        :rtype: Entity
        """
        if values is None:
            values = {}
        elif not isinstance(values, dict):
            values = {self.primary: values}

        if check:
            self.check(values)
        return Entity(self, {key: values.get(key, self._defaults[key]) for key in self._names})


def datetime_serializer(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    raise TypeError("Type {} not json serializable".format(type(dt)))


class Entity:
    """
    Entity represents objects in the world. It MUST be structured as a shallow json object (single depth). Deeper
    nested fields can be stored, but won't be accessible directly in general.
    """
    def __init__(self, schema, values):
        """
        :param schema: a Schema object holds the definition of the schema
        :param values: a dictionary of key value pairs
        """
        self.schema = schema
        self.__dict__.update(values)
        self._json = json.dumps(OrderedDict(sorted(self.data.items())), default=datetime_serializer)
        self._uuid = str(uuid.uuid5(uuid.NAMESPACE_X500, str(self.primary)))
        self._hash_code = hash(self._uuid)

    def __str__(self):
        return "({}){}".format(self.schema.name, self.primary)

    def __repr__(self):
        return self.json

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.uuid == other.uuid
        elif isinstance(other, dict):
            return self.json == json.dumps(OrderedDict(sorted(other.items())), default=datetime_serializer)
        else:
            return False

    def __hash__(self):
        return self._hash_code

    @property
    def primary(self):
        return getattr(self, self.schema.primary)

    @property
    def data(self):
        return {key: getattr(self, key) for key in self.schema.keys}

    @property
    def json(self):
        return self._json

    @property
    def uuid(self):
        return self._uuid


default_schema = Schema('default', ['name'], {'name': 'Text'})
empty_entity = default_schema.entity()
