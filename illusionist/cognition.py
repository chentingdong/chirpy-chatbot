import json
import requests
from flask import session

from illusionist.luke import Luke
from illusionist.models.agent import Agent

from python_utils.config import server_config
from python_utils.logger import logger_console
from illusionist.bot_engine import BotEngine
from uuid import uuid4
import sys
from illusionist.customerrules import *


class Cognition():
    luke = Luke()
    # overwritten by app_config
    start_over = ['hi', 'start over']

    def get_answer(self, utterance, context):
        answer = BotEngine().answer(utterance, context)
        logger_console.info('"Q: {}"; "A: {}"'.format(utterance, answer.get('pretext')))
        logger_console.info('"current_bot: {}: current_node: {}"'.format(
            context.get_local('current_bot'),
            context.get_local('current_node')
        ))
        context.converstion_history.append({
            'user': utterance,
            'agent': answer.get('pretext')
        })
        return answer

    def check_conversation_id(self, context):
        if not context.get_local('conversation_id'):
            context.set_local('conversation_id', str(uuid4()))

        if context.bot_history:
            last_request_bot = context.bot_history[-1]

            if last_request_bot not in ['converse']:
                context.set_local('conversation_id', str(uuid4()))

    def in_conversation(self, context):
        current_bot = context.get_local('current_bot')
        return current_bot

    def new_conversation(self, context):
        agent_config = session.get('agent_config', {})
        BotEngine().assign_bot(context, bot_name=agent_config.get('index'))
        context.converstion_history = []
        self.check_conversation_id(context)

    def find_bot(self, utterance, context):
        if not utterance:
            self.new_conversation(context)
            return

        if self.is_startover(utterance):
            self.new_conversation(context)
            return

        if self.in_conversation(context):
            return

        # Check for all applicable customer rules and apply them
        customer_rule_applied = self.apply_customer_rules(context)
        if customer_rule_applied:
            return

        # search bot with exact utterance matching, to handle specific cases that luke can't handle
        # luke/spacy search uses 'converse' as the default bot, so we exclude it here.
        self.luke_find_special_bot(utterance, context)
        if context.get_local('current_bot', 'converse') != 'converse':
            return

        self.check_conversation_id(context)
        self.luke_find_bot(utterance, context)

    def apply_customer_rules(self, context):
        agent_config = session.get('agent_config', {})
        customer_rules = agent_config.get('customer_rules', {})
        for customer_rule, services in customer_rules.items():
            cls = getattr(sys.modules[__name__], customer_rule)
            logger_console.info('Applying customer rule: {}'.format(customer_rule))
            return cls().apply(context, services)

    def luke_find_special_bot(self, utterance, context):
        search_url_server = server_config.get('luke', {}).get('search_url')
        agent_config = session.get('agent_config')
        search_url = agent_config.get('search_url', search_url_server)

        luke_answer = self.luke.ask(utterance, context, search_url)
        bot_name = luke_answer.get('code')
        BotEngine().assign_bot(context, bot_name=bot_name)

    def luke_find_bot(self, utterance, context):
        answer_url_server = server_config.get('luke', {}).get('answer_url')
        agent_config = session.get('agent_config')
        answer_url = agent_config.get('answer_url', answer_url_server)

        luke_answer = self.luke.ask(utterance, context, answer_url)

        luke_code = luke_answer.get('code')
        converse_codes = ['converse', 'greeting', 'bye', 'clarify', 'not_related']
        if luke_code in converse_codes or luke_code.startswith('jira'):
            bot_name = 'converse'
        else:
            bot_name = luke_code

        BotEngine().assign_bot(context, bot_name=bot_name)

    def error_answer(self, context):
        BotEngine().assign_bot(context, None)
        agent_id = context.get_local('agent_id')
        agent_config = Agent().get_config(agent_id)
        error_message = agent_config.get('error_message', 'Sorry, I do not understand.')

        answer = {
            'code': 'error',
            'pretext': error_message
        }
        return answer

    # Below come from v1, to be deprecated
    def classify_intents(self, utterance, url):
        post_data = json.dumps({
            "utterance": utterance,
            "session_context": {}
        })
        context = session.get('context', {})
        headers = {
            'Content-Type': 'application/json',
            'Illusionist-Request-Id': context.get_local('request_id')
        }
        response = requests.post(url=url, data=post_data, headers=headers)
        context.set_local('luke_request_id', response.headers.get('Request-Id'))
        ret = response.json().get('result')
        return ret

    def is_startover(self, utterance):
        # if agent_config specifies start over list, use strict match, otherwise ask luke
        agent_config = session.get('agent_config', {})
        start_over = agent_config.get('start_over', self.start_over)

        if start_over:
            start_over = [text.lower() for text in start_over]
            is_startover = utterance.lower() in start_over
            ret = is_startover
        else:
            url = server_config.get('luke').get('startover_url', '')
            ret = self.classify_intents(utterance, url)

        return ret

    def is_yes_no(self, utterance):
        url = server_config.get('luke').get('yes_no_url')
        ret = self.classify_intents(utterance, url)
        return ret

    def is_greeting(self, utterance):
        url = server_config.get('luke').get('greeting_url')
        ret = self.classify_intents(utterance, url)
        return ret

    def is_bye(self, utterance):
        url = server_config.get('luke').get('bye_url')
        ret = self.classify_intents(utterance, url)
        return ret

    def is_thanks(self, utterance):
        url = server_config.get('luke').get('thanks_url')
        ret = self.classify_intents(utterance, url)
        return ret


cog = Cognition()
