import copy
import sys
import json
from string import Template

from flask import session
from python_utils.logger import logger_console, logger
from illusionist.context import Context
from illusionist.models.agent import Agent
from illusionist.luke import SemanticMatch
from illusionist.models.action import Action
from illusionist.actions import *
from illusionist.services.servicenow import ServiceNowForm


class BotEngine:
    def __init__(self):
        self.semantic_match = SemanticMatch()
        self.threshold = self.semantic_match.threshold

    def answer(self, utterance, context):
        bot_name = context.get_local('current_bot')
        bot = self.find_bot_by_name(bot_name)

        if not bot and utterance:
            agent_config = session.get('agent_config', {})
            if agent_config.get('index'):
                BotEngine().assign_bot(context, bot_name=agent_config.get('index'))
            else:
                return self.answer_for_error(context)

        transition_success, node = self.transition(utterance, bot, context)

        answer = copy.deepcopy(node['data'])
        self.remember_context_var(utterance, answer, context)

        if node.get('data', {}).get('transition', ''): # avoid empty transition field error
            transition_success, node = self.check_goto_bot(utterance, node, context)
            answer = copy.deepcopy(node['data'])

        if not transition_success:
            answer['pretext'] = bot.params['answer_not_related']
        elif node['name'] == 'Converse':
            answer = self.answer_from_converse(answer, context)
        elif node['name'] == 'Dialogue':
            answer = self.answer_from_dialogue(answer, context)
        elif node['name'] == 'Action':
            answer = self.answer_from_action(node, context)
        else:
            logger_console.warn('Bot flow error')
            answer['pretext'] = bot.params['answer_error']
            self.assign_bot(context, None)

        self.answer_from_context(answer, context)

        return answer

    def remember_context_var(self, utterance, answer, context):
        context_var = answer.get('context_var')
        if not context_var:
            return

        mode = answer.get('context_var_mode', 'update')

        # TODO: maybe a special node to collect form dict
        context_var_parts = context_var.split(',')
        if len(context_var_parts) > 1:
            # like (form, {'val_1': 'asdf'}).
            # using previous node's name to automatically generate context_var key for the form.
            (key, values) = context_var_parts
            if mode == 'reset':
                context.set_local(key, {})
                return

            prev_context_var_dict = context.get_local(key, {})
            incoming_context_var_dict = json.loads(context_var_parts[1])
            auto_context_var_dict = {context.converstion_history[-1]['agent']: utterance}
            context_var_dict = {**prev_context_var_dict, **incoming_context_var_dict, **auto_context_var_dict}
            context.set_local(key, context_var_dict)

        else:
            # like: short_description.
            # TODO, we may not need 'update' mode in UI. update = reset + append.
            prev_context_var_value = context.get_local(answer['context_var'], '')
            if mode == 'reset':
                query = ''
            elif mode == 'append':
                query = prev_context_var_value + '. ' + utterance
            else:
                query = utterance

            context.set_local(answer['context_var'], query)

    def generate_context_var_key(self, name):
        return name.replace('\s+', '_').lower()

    def answer_for_error(self, context):
        self.assign_bot(context, None)
        agent_id = context.get_local('agent_id')
        agent_config = Agent().get_config(agent_id)

        error_message = "Sorry, I didn't get that, please try again."
        answer = {
            'name': 'error',
            'pretext': agent_config.get('error_message') or error_message
        }

        if context.get_local('luke_answer', {}).get('data', {}).get('code', '') == 'note_related':
            answer['pretext'] = context.get_local('luke_answer', {}).get('data', {}).get('utterance')

        return answer

    def answer_for_jira_commands(self, context):
        luke_answer = context.get_local('luke_answer')
        answer = {
            'pretext': luke_answer['data']['utterance'],
            'answer_action': luke_answer['code'],
            'template_action': 'jira-command'
        }
        return answer

    def answer_from_converse(self, answer, context):
        luke_answer = context.get_local('luke_answer')
        context.set_local('domain', luke_answer['data']['domain'].upper())
        luke_code = luke_answer['code']

        answer['pretext'] = self.determine_pretext(answer, context)

        # if luke_code.startswith('jira'):
        #     return self.answer_for_jira_commands(context)

        if luke_code == 'clarify':
            answer['template_action'] = 'text-buttons'
            answer['answer_action'] = luke_answer['data']

        elif luke_code == 'form':
            answer['template_action'] = 'link-buttons'
            answer['answer_action'] = ServiceNowForm(context).build_links(luke_answer['data'])

        return answer

    def answer_from_dialogue(self, answer, context):
        answer['pretext'] = self.determine_pretext(answer, context)
        return answer

    def determine_pretext(self, answer, context):
        """
        Give preference to pretext in Template if available else return utterance from luke
        """
        pretext_bot = Template(answer.get('pretext', '')).safe_substitute(context.local_variables)
        pretext_luke = context.get_local('luke_answer', {}).get('data', {}).get('utterance', '')

        return pretext_bot if pretext_bot != '' else pretext_luke

    def answer_from_action(self, node, context):
        """
        action node doesn't answer user, it pass action result to children dialogue nodes.
        """
        # in action node
        action = node.get('data', {}).get('action')
        status, answer_action = self.bot_action(action, context)
        template_action = node.get('data', {}).get('template', '')

        # transit to child dialog. with goto, bot can be different from last dialogue state.
        bot_name = context.get_local('current_bot')
        bot = self.find_bot_by_name(bot_name)
        transition_success, child = self.transition(status, bot, context)

        if not transition_success:
            answer = copy.deepcopy(node['data'])
            return answer

        # template string replacement for inline template
        answer = child['data']

        if template_action != '':
            answer['template_action'] = template_action
        if answer_action:
            answer['answer_action'] = answer_action

        if answer.get('template_action') == 'inline':
            answer['pretext'] = answer['pretext'].format(**answer_action)

        logger_console.debug('Action bot name="{bot}" node="{node}" returns answer: "{ans}"'.format(
            bot=context.get_local('current_bot'),
            node=context.get_local('current_node'),
            ans=answer))

        return answer

    def answer_from_context(self, answer, context):
        """
        replace pretext pattern with context variables
        """
        # pretext = answer.get('pretext', answer.get('answer', ''))
        pretext = answer.get('pretext', '')
        if pretext == '':
            logger_console.error('empty pretext')
        answer['pretext'] = pretext.format(**context.local_variables)

    @logger.exception()
    def bot_action(self, action: str, context: Context):
        action_obj = Action.query.filter_by(name=action).first()
        if not action_obj:
            logger_console.warn('Action not found {}'.format(action))
        cls = getattr(sys.modules[__name__], action)
        code, data = cls.run(action_obj, context)

        return code, data

    @logger.exception()
    def transition(self, utterance, bot, context):
        node = self.get_current_node(context)
        children = self.find_children_nodes(bot, node)
        wildcard_node = None
        max_score_node = None
        max_score = self.threshold
        for child in children:
            options = child['data']['question'].split('||')
            options = [x.strip() for x in options]
            if '*' in options:
                wildcard_node = child
            score = self.semantic_match.match(utterance, options)
            if score > max_score:
                max_score = score
                max_score_node = child

        if max_score_node is not None:
            node = max_score_node
        elif wildcard_node:
            node = wildcard_node
        else:
            node = node

        context.set_local('current_node', node['data']['name'])
        context.state_history.append(str(bot.id) + '-' + node['data']['name'])

        transition_success = False
        if max_score > self.threshold or wildcard_node:
            transition_success = True

        self.check_end_node(bot, node, context)
        return transition_success, node

    def check_goto_bot(self, utterance, node, context) -> (bool, any):
        goto_bot_name = node.get('data', {}).get('transition')
        goto_bot = self.find_bot_by_name(goto_bot_name)
        if goto_bot:
            self.assign_bot(context, bot_name=goto_bot_name)
            transition_success, node = self.transition(utterance, goto_bot, context)
            return transition_success, node
        else:
            return False, node

    def find_bot_by_name(self, name):
        bots = session.get('bots')
        for bot in bots:
            if bot.name == name:
                return bot
        return None

    def find_bot_id_by_name(self, name):
        bot = self.find_bot_by_name(name)
        return bot.id or None

    def find_bot_by_id(self, bots, id):
        for bot in bots:
            if bot.id == id:
                return bot
        return None

    def assign_bot(self, context, bot_name=None):
        if not bot_name:
            return None

        bot = self.find_bot_by_name(bot_name)
        if not bot:
            logger_console.error("Bot not found, {}".format(bot_name))
            return None

        context.state_history.append(str(bot.id) + '-start')
        context.bot_history.append(bot_name)
        context.set_local('bot', bot)
        context.set_local('current_node', 'start')

        context.set_local('current_bot', bot_name)
        context.set_local('current_bot_id', bot.id)

    def get_current_node(self, context):
        bot_name = context.get_local('current_bot')
        node_name = context.get_local('current_node')
        bot = self.find_bot_by_name(bot_name)
        node = self.find_node_by_name(bot, node_name)
        return node

    def find_node_by_name(self, bot, node_name):
        nodes = bot.workflow['nodes']
        for id in nodes:
            node = nodes[id]
            if node['data']['name'] == node_name:
                return node

    def find_children_nodes(self, bot, node) -> list:
        nodes = bot.workflow['nodes']
        output_connections = node['outputs']['output']['connections']
        output_node_ids = [output_connection['node'] for output_connection in output_connections]
        children_nodes = [nodes[str(node_id)] for node_id in output_node_ids]
        return children_nodes

    def check_end_node(self, bot, node, context):
        children = self.find_children_nodes(bot, node)
        for child in children:
            if child['data']['name'] == 'end':
                context.state_history.append(str(bot.id) + '-end')
                context.set_local('bot', None)
                context.set_local('current_node', None)
                context.set_local('current_bot', None)
                return
