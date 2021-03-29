# TODO: to be deprecated in illusionist 3.0. Delete with engine.py.

from typing import List
from uuid import uuid3
from illusionist.helpers.util import NAMESPACE_ILLUSIONIST


class Schema(object):
    category = 'other'
    json = {'type': 'object',
            'properties': {'category': {'type': 'string'},
                           'content': {'type': 'string'},
                           'content_json': {'type': 'string'},
                           'schema': {'type': 'object'},
                           'uuid': {'type': 'string'},
                           'explanation': {'type': 'object'},
                           'probability': {'type': 'float'}
                           }
            }

    @classmethod
    def encode(cls, utterance: str, uid: str='', explanation: str='', content_json: str='') -> object:
        if uid == '':
            uid = str(uuid3(NAMESPACE_ILLUSIONIST, utterance))
        return {'category': cls.category,
                'content': utterance,
                'content_json': content_json,
                'schema': cls.json['properties']['content'],
                'uuid': uid,
                'explanation': {'description': explanation},
                'probability': 1.0}


class AnswerSchema(Schema):
    category = 'answer'
    json = {'type': 'object',
            'properties': {'category': {'type': 'string'},
                           'content': {'type': 'object',
                                       'properties': {'title': {'type': 'string'},
                                                      'summary': {'type': 'string'},
                                                      'date': {'type': 'string'},
                                                      'url': {'type': 'string'}
                                                      }
                                       },
                           'schema': {'type': 'object'},
                           'uuid': {'type': 'string'},
                           'explanation': {'type': 'object'},
                           'probability': {'type': 'float'}
                           }
            }

    @classmethod
    def encode(cls, prob: float, title: str, summary: str, date: str, url: str, uid: str='', explanation: str='') -> object:
        if uid == '':
            uid = str(uuid3(NAMESPACE_ILLUSIONIST, summary))
        return {'category': cls.category,
                'content': {'title': title, 'summary': summary, 'date': date, 'url': url},
                'schema': cls.json['properties']['content'],
                'uuid': uid,
                'explanation': {'description': explanation},
                'probability': prob}


class ChoicesSchema(Schema):
    category = 'choices'
    json = {'type': 'object',
            'properties': {'category': {'type': 'string'},
                           'content': {'type': 'object',
                                       'properties': {'question': {'type': 'string'},
                                                      'choices': {'type': 'array',
                                                                  'items': {'type': 'string'}
                                                                  }
                                                      }
                                       },
                           'schema': {'type': 'object'},
                           'uuid': {'type': 'string'},
                           'explanation': {'type': 'object'},
                           'probability': {'type': 'float'}
                           }
            }

    @classmethod
    def encode(cls, question: str, choices: List[str], uid: str='', explanation: str='') -> object:
        if uid == '':
            uid = str(uuid3(NAMESPACE_ILLUSIONIST, question))
        return {'category': cls.category,
                'content': {'question': question, 'choices': choices},
                'schema': cls.json['properties']['content'],
                'uuid': uid,
                'explanation': {'description': explanation},
                'probability': 1.0}


class HelpfulChoicesSchema(Schema):
    category = 'helpful_choices'
    json = {'type': 'object',
            'properties': {'category': {'type': 'string'},
                           'content': {'type': 'string',
                                       'properties': {'question': {'type': 'string'},
                                                      'choices': {'type': 'array',
                                                                  'items': {'type': 'string'}
                                                                  }
                                                      }
                                       },
                           'schema': {'type': 'object'},
                           'uuid': {'type': 'string'},
                           'explanation': {'type': 'object'},
                           'probability': {'type': 'float'}
                           }
            }

    @classmethod
    def encode(cls, question: str, choices: List[str], uid: str='', explanation: str='') -> object:
        if uid == '':
            uid = str(uuid3(NAMESPACE_ILLUSIONIST, question))
        return {'category': cls.category,
                'content': {'choices_header': question, 'helpful_choices': choices},
                'schema': cls.json['properties']['content'],
                'uuid': uid,
                'explanation': {'description': explanation},
                'probability': 1.0}



class IncidentSchema(Schema):
    category = 'incident'
    json = {'type': 'object',
            'properties': {'category': {'type': 'string'},
                           'content': {'type': 'object',
                                       'properties': {'sys_id': {'type': 'string'}}
                                       },
                           'schema': {'type': 'object'},
                           'uuid': {'type': 'string'},
                           'explanation': {'type': 'object'},
                           'probability': {'type': 'float'}
                           }
            }

    @classmethod
    def encode(cls, incident_sys_id: str, prob: float, uid: str = '', explanation: str = '') -> object:
        if uid == '':
            uid = str(uuid3(NAMESPACE_ILLUSIONIST, incident_sys_id))
        return {'category': cls.category,
                'content': {'sys_id': incident_sys_id},
                'schema': cls.json['properties']['content'],
                'uuid': uid,
                'explanation': {'description': explanation},
                'probability': prob}


class LinksSchema(Schema):
    category = 'links'
    json = {'type': 'object',
            'properties': {'category': {'type': 'string'},
                           'content': {'type': 'string',
                                       'properties': {'question': {'type': 'string'},
                                                      'links': {
                                                              'type': 'array',
                                                              'items': {
                                                                'type': 'object',
                                                                'properties': {
                                                                  'title': { 'type': 'string' },
                                                                  'url': { 'type': 'string' },
                                                                  'location': { 'type': 'string' }
                                                                }
                                                              }
                                                            }
                                                      }
                                       },
                           'schema': {'type': 'object'},
                           'uuid': {'type': 'string'},
                           'explanation': {'type': 'object'},
                           'probability': {'type': 'float'}
                           }
            }

    @classmethod
    def encode(cls, question: str, links: List[str], uid: str='', explanation: str='') -> object:
        if uid == '':
            uid = str(uuid3(NAMESPACE_ILLUSIONIST, question))
        return {'category': cls.category,
                'content': {'question': question, 'links': links},
                'schema': cls.json['properties']['content'],
                'uuid': uid,
                'explanation': {'description': explanation},
                'probability': 1.0}



class CategorizedIncidentSchema(Schema):
    category = 'categorized_incident'

    json = {'type': 'object',
            'properties': {'category': {'type': 'string'},
                           'content': {'type': 'string',
                                       'properties': {'question': {'type': 'string'},
                                                      'categorized_incident': {
                                                          'type': 'array',
                                                          'items': {
                                                              'type': 'object',
                                                              'properties': {
                                                                  'short_description': {'type': 'string'},
                                                                  'description': {'type': 'string'},
                                                                  'u_service': {'type': 'string'},
                                                                  'u_subservice': {'type': 'string'},
                                                                  'u_category': {'type': 'string'},
                                                                  "u_ticket_type": {'type': 'string'},
                                                                  "contact_type": {'type': 'string'},
                                                                  "opened_by_group": {'type': 'string'},
                                                                  "caller_id": {'type': 'string'},
                                                                  "display_value": {'type': 'string'}
                                                              }
                                                          }
                                                      }
                                                      }
                                       },
                           'schema': {'type': 'object'},
                           'uuid': {'type': 'string'},
                           'explanation': {'type': 'object'},
                           'probability': {'type': 'float'}
                           }
            }

    @classmethod
    def encode(cls, incident_response: str, incident_url: str, uid: str = '', explanation: str = '') -> object:
        if uid == '':
            uid = str(uuid3(NAMESPACE_ILLUSIONIST, incident_response))
        return {'category': cls.category,
                'content': {'incident_response': incident_response, 'incident_url': incident_url},
                'schema': cls.json['properties']['content'],
                'uuid': uid,
                'explanation': {'description': explanation},
                'probability': 1.0}
