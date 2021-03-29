from flask import request, jsonify, session
from python_utils.flask_sqlalchemy_base import db
from illusionist.models.app import App
from python_utils.config import server_config
from illusionist.bot_engine import BotEngine
from illusionist.cognition import Cognition
from illusionist.context import Context
from illusionist.models.agent import Agent
from illusionist.response import Response
from python_utils.logger import logger, logger_console
from illusionist.apis.bp import bp


@bp.route('/api/1/check_agent_driven', methods=['POST'])
def check_index_bot():
    request_json = request.json
    response = Response()
    response.success()
    agent_id = int(request_json.get('agent_id'))
    agent_config = session_agent_config(agent_id)
    agent_driven = agent_config.get('agent_driven', False)
    response.add_payload('agent_driven', agent_driven)
    return jsonify(**response.object)


@bp.route('/answers/<app_uid>', methods=['POST'])
@logger.api_access()
def ask_by_app_uid(app_uid):
    request_json = request.json
    # TODO: filter by app routing settings
    agent = db.session.query(Agent).join(App, App.id == Agent.app_id).filter_by(uid=app_uid).first()
    agent_id = agent.id
    response = ask(agent_id, request_json)
    logger_console.debug('/answers/{}\nrequests: {}\nresponse: {}'.format(app_uid, request_json, response))
    return response


@bp.route('/api/1/ask', methods=['POST'])
@logger.api_access()
def ask_by_agent_id():
    request_json = request.json
    agent_id = int(request_json.get('agent_id'))
    response = ask(agent_id, request_json)
    return response


def ask(agent_id, request_json, testing=False):
    session_agent_config(agent_id)

    context = get_context()
    context.set_local('agent_id', agent_id)
    set_session_context(request_json, context)
    load_session_bots(context)

    utterance = context.get_local('utterance')
    Cognition().find_bot(utterance, context)

    response = build_response(context)
    debug_info(context, response)
    reset_answer(context)
    return jsonify(**response.object) if not testing else response.object


def load_session_bots(context):
    agent_id = str(context.get_local('agent_id'))
    agent = Agent.query.filter_by(id=agent_id).one_or_none()
    bots = list(agent.bots)
    session.setdefault('bots', bots)


def get_context():
    context = session.get('context')

    if not context:
        context = Context()
        session.setdefault('context', context)

    session_data = session.get('data')
    if not session_data:
        session.setdefault('data', {})
    # session_data['dialog_state'] = context.state_history[-1]

    return context


def set_session_context(request_json, context):
    utterance = request_json.get('utterance', '')
    instance_name = request_json.get('instance_name', '')
    virtual_agent_user_id = request_json.get('virtual_agent_user_id', 'virtual_agent')
    user_info = request_json.get('user_info', {})
    first_name = user_info.get('first_name', '')
    chatbot_user_id = request_json.get('user_id', '')
    country = user_info.get('country', '')
    group = user_info.get('group', '')
    company = user_info.get('company', '')
    client_id = request_json.get('client_id', 'slack-0')
    debug = bool(request_json.get('debug', 'false'))
    agent_id = context.get_local('agent_id', 41)
    app = db.session.query(App).join(Agent, App.id == Agent.app_id).filter(Agent.id == agent_id).first()
    org_id = app.org_id if app else ''

    request_id = request.environ.get("FLASK_REQUEST_ID")

    context.set_local('virtual_agent_user_id', virtual_agent_user_id)
    context.set_local('chatbot_user_id', chatbot_user_id)
    context.set_local('client_id', client_id)
    context.set_local('agent_id', agent_id)
    context.set_local('instance_name', instance_name)
    context.set_local('first_name', first_name)
    context.set_local('country', country)
    context.set_local('group', group)
    context.set_local('company', company)
    context.set_local('request_id', request_id)
    context.set_local('utterance', utterance)
    context.set_local('debug', debug)
    context.set_local('org_id', org_id)


def build_response(context):
    response = Response()
    utterance = context.get_local('utterance')
    answer = Cognition().get_answer(utterance, context)

    response.session_id = session.sid
    response.conversation_id = context.get_local('conversation_id')
    request_id = request.environ.get("FLASK_REQUEST_ID")
    response.request_id = request_id
    response.luke_request_id = context.get_local('luke_request_id')
    response.add_payload('entity_sys_id', context.get_local('entity_sys_id'))
    response.add_payload('state_history', context.state_history)
    response.add_payload('bot_history', context.bot_history)
    response.add_payload('answer', answer)

    response.success()

    logger_console.info("Ask api response: {}".format(response.payloads['answer']))
    return response


def debug_info(context, response):
    if not server_config['configs']['debug']:
        return None

    bot_name = context.get_local('current_bot')
    if not bot_name:
        response.add_payload('current_bot', '{} not found'.format(bot_name))
        return
    response.add_payload('current_bot', bot_name)
    response.add_payload('current_bot_id', context.get_local('current_bot_id'))
    bot = BotEngine().find_bot_by_name(bot_name)
    node_name = context.get_local('current_node', 'end')
    node = BotEngine().find_node_by_name(bot, node_name)
    response.add_payload('current_node_id', node['id'])
    response.success()

    logger_console.info("Ask api response: {}".format(response.payloads['answer']))


def session_agent_config(agent_id):
    agent_config = session.get('agent_config', {})
    if not agent_config:
        agent = Agent.query.filter_by(id=agent_id).one_or_none()

        agent_config = agent.parameters
        session.setdefault('agent_config', agent_config)
    return agent_config


def reset_answer(context):
    context.set_local('answer', {})
