# TODO: write this into a fake luke server
import json
import requests
from python_utils.logger import logger, logger_console
from python_utils.config import server_config
from flask import session
from urllib.parse import urlparse
import os.path


class Luke:
    default_threshold = 0.5

    def get_nlp_threshold(self, answer_url):
        # passing threshold to luke corresponding agent/apis. support 2 kind of agents where answer url is:
        agent_config = session.get('agent_config')
        path = urlparse(answer_url).path
        path_parts = os.path.normpath(path).split(os.path.sep)
        if len(path_parts) > 3 and path_parts[3] == 'bot_search':
            # "search_url": "http://luke-dev.nevaai.com:6001/api/apps/bot_search/spacy/list"
            nlp = path_parts[4]
            nlp_threshold = agent_config.get(nlp + '_threshold', self.default_threshold)
            return nlp_threshold
        else:
            # "answer_url": "http://luke-dev.nevaai.com/agent/10/answer"
            # answer url doesn't require a threshold yet
            return self.default_threshold

    @logger.exception()
    def ask(self, utterance, context, answer_url):
        headers = {
            'Content-Type': 'application/json',
            'Illusionist-Request-Id': context.get_local('request_id'),
            'Access-Control-Allow-Origin': '*'
        }
        # Must match luke ask and bot_search schema. Can add, but should not change or delete keys.
        post_data = {
            "utterance": utterance,
            "session_id": session.sid,
            "session_context": {
                'threshold': self.get_nlp_threshold(answer_url),
                # TODO: remove once luke bot_search is refactored
                'app_id': context.get_local('agent_id'),
                'agent_id': context.get_local('agent_id'),
                'first_name': context.get_local('first_name'),
                'country': context.get_local('country')
            }
        }

        logger_console.debug('url={}, data={}'.format(answer_url, post_data))

        response = requests.post(url=answer_url, data=json.dumps(post_data), headers=headers)

        if response.status_code != 200:
            raise Exception("luke call failed: url={}, data={}, response.status_code={}, response.text={}".format(
                answer_url, post_data, response.status_code, response.text))

        if response.headers:
            request_id = response.headers.get('Request-Id')
        else:
            request_id = session.get('request_id')
        context.set_local('luke_request_id', request_id)

        luke_answer = response.json()
        context.set_local('luke_answer', luke_answer)

        logger_console.info('luke answer: {}'.format(luke_answer))

        session_data = session.get('data')
        session_data['luke_release_version'] = luke_answer.get('release_version', '')

        return luke_answer


class SemanticMatch:
    match_url_server_default = server_config.get('luke').get('match_url')
    match_unit_default = 'list' # luke or spacy
    default_threshold = 0.5

    def __init__(self):
        agent_config = session.get('agent_config')
        self.match_url_agent_default = agent_config.get('match_url', self.match_url_server_default)
        self.match_url = agent_config.get('match_url', self.match_url_agent_default)

    @property
    def threshold(self):
        agent_config = session.get('agent_config', {})

        if 'spacy' in self.match_url:
            threshold = agent_config.get('spacy_threshold', self.default_threshold)
        else:
            threshold = agent_config.get('luke_threshold', self.default_threshold)

        return threshold

    def match(self, utterance, utterances):
        if not utterance:
            return 0.0

        data = {
            'utterance': utterance,
            'utterances': utterances
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.post(self.match_url, data=json.dumps(data), headers=headers)
        score = response.json().get('score', 0.0)

        return score
