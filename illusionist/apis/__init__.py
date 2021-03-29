import flask_restless
from python_utils.flask_sqlalchemy_base import db
from illusionist.models.app import App
from illusionist.models.agent import Agent
from illusionist.models.service import Service
from illusionist.models.bot import Bot, TestBot
from illusionist.models.action import Action
from illusionist.models.agent_bot import AgentBot
from illusionist.models.bot_action import BotAction
from illusionist.models.user import User
from illusionist.models.role import Role


def agent_get_many_postprocessor(result={}, **kw):
    agents = result.get('objects')
    for agent in agents:
        bots = []
        for bot in agent.get('bots'):
            bots.append({
                'id': bot['id'],
                'name': bot['name']
            })
        agent['bots'] = bots


def bot_get_single_postprocessor(result={}, **kw):
    agents = result.get('agents')
    agent_ids = [agent.get('id') for agent in agents]
    result['agents'] = agent_ids


def bot_get_many_postprocessor(result={}, **kw):
    bots = result.get('objects')
    for bot in bots:
        bot['agents'] = [agent['id'] for agent in bot['agents']]
        bot['workflow'] = {}
        if bot['botTests']:
            bot.setdefault('test_passed', bot['botTests'][0]['test_passed'])
        else:
            bot.setdefault('test_passed', None)
        del bot['botTests']


def bot_patch_single_preprocessor(data=None, **kw):
    agent_ids = data['agents']
    agents = [{'id': agent_id} for agent_id in agent_ids]
    agents.sort(key=id, reverse=True)
    data['agents'] = agents


result_per_page = 200

api_manager = flask_restless.APIManager(flask_sqlalchemy_db=db)


api_manager.create_api(User,
                       collection_name='user',
                       methods=['GET', 'POST', 'PUT', 'DELETE'])
api_manager.create_api(Role,
                       collection_name='role',
                       methods=['GET', 'POST', 'PUT', 'DELETE'])
api_manager.create_api(Action,
                       collection_name='action',
                       results_per_page=result_per_page,
                       methods=['GET', 'POST', 'PUT', 'DELETE'])
api_manager.create_api(Service,
                       results_per_page=result_per_page,
                       collection_name='service',
                       methods=['GET', 'POST', 'PUT', 'DELETE'])
api_manager.create_api(App,
                       collection_name='app',
                       results_per_page=result_per_page,
                       methods=['GET', 'POST', "PUT", "DELETE"])
api_manager.create_api(Agent,
                       collection_name='agent',
                       exclude_columns=['agent_bots', 'services'],
                       results_per_page=result_per_page,
                       methods=['GET', 'POST', "PUT", "DELETE"],
                       postprocessors={
                           'GET_MANY': [agent_get_many_postprocessor]
                       })
api_manager.create_api(AgentBot,
                       collection_name='agent_bot',
                       methods=["GET", "POST", "PUT", "DELETE"])
api_manager.create_api(BotAction,
                       collection_name='bot_action',
                       methods=["GET", "POST", "PUT", "DELETE"])
api_manager.create_api(Bot,
                       collection_name='bot',
                       methods=["GET", "POST", "PUT", "DELETE"],
                       results_per_page=0,
                       exclude_columns=['bot_agents'],
                       validation_exceptions=[ValueError],
                       preprocessors={
                           'PUT_SINGLE': [bot_patch_single_preprocessor],
                           'POST': [bot_patch_single_preprocessor]
                       },
                       postprocessors={
                           'GET_SINGLE': [bot_get_single_postprocessor],
                           'PUT_SINGLE': [bot_get_single_postprocessor],
                           'GET_MANY': [bot_get_many_postprocessor],
                           'POST': [bot_get_single_postprocessor],
                       })
api_manager.create_api(TestBot,
                       collection_name='test_bot',
                       methods=['GET', 'POST', 'PUT', 'DELETE'])
