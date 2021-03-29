import sys

from flask import request, jsonify, make_response
from illusionist.models.service import Service
from illusionist.apis.bp import bp
from illusionist.models.agent import Agent
from illusionist.models.bot import Bot
from illusionist.actions import *


@bp.route('/api/1/clone_agent', methods=['POST'])
def clone_agent():
    clone_validate()

    # TODO: breakdown this function
    # clone agent
    from_agent_id = request.json.get('agent_id')
    agent = Agent.query.filter_by(id=from_agent_id).one_or_none()
    agent.clone()

    # clone bots
    bots = list()
    services = set()
    from_bots = request.json.get('bots')
    for from_bot in from_bots:
        bot = Bot.query.filter_by(id=from_bot['id']).one_or_none()
        for action in bot.actions:
            action_cls = getattr(sys.modules[__name__], action.action_type)
            service = Service.query.filter_by(name=action_cls.service_name, agent_id=from_agent_id).one_or_none()
            if service:
                services.add(service)
        bot.clone(agent)
        bots.append(bot)

    # clone services
    for service in services:
        service.clone(agent)

    # response
    status = 200
    resp = {
        'agent': {'id': agent.id, 'name': agent.name},
        'bots': [{'id': bot.id, 'name': bot.name} for bot in bots],
        'services': [{'id': service.id, 'name': service.name, 'agent_id': service.agent_id} for service in services]
    }
    return make_response(jsonify(**resp), status)


def clone_validate():
    return True
