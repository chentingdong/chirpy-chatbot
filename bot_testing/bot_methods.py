from bot_testing.ask import ask_api
import uuid
from python_utils.logger import logger_console
from illusionist.app import create_app
from illusionist.models.app import App
from illusionist.models.agent_bot import AgentBot
from illusionist.models.bot import Bot
from illusionist.models.bot import TestBot
from python_utils.flask_sqlalchemy_base import db


def get_recorded_data(agent_id):
    results = (db.session.query(Bot.id, TestBot.name, TestBot.test_set)
         .filter(TestBot.id == Bot.id)
         .filter(Bot.id == AgentBot.bot_id)
         .filter(AgentBot.agent_id == agent_id)
         .filter(Bot.searchable == 1)
         .all())
    return results

def diff_status(diff):
    return False if len(diff.keys()) > 0 else True


def update_test_status_db(diff, bot_id):
    # updating status in database table
    if len(diff.keys()) > 0:
        db.session.query(TestBot).filter(TestBot.id == bot_id).update({'test_passed': 0})
        db.session.commit()
        logger_console.error('Test Status : ' + 'Fail')
    else:
        db.session.query(TestBot).filter(TestBot.id == bot_id).update({'test_passed': 1})
        db.session.commit()
        logger_console.info('Test Status : ' + 'Pass')


def get_expected_utterances(response):
    # getting expected utterances of recorded test_set
    utterances = list()
    for utterance in response:
        if utterance.get('me', None):
            utterances.append(utterance.get('message', None))
    logger_console.info('Recorded Utterances: {}'.format(utterances))
    return utterances


def get_expected_response(response):
    # getting expected response object of recorded test_set
    expected_response = list()
    for utterance in response:
        if utterance.get('them', None):
            expected_response.append(utterance.get('message', None))
    return expected_response


def get_actual_response(utterances, bot_id, bot_name):
    # getting Actual response from ask endpoint
    actual_response = list()
    sys_id = uuid.uuid1()
    for utterance in utterances:
        response = ask_api(sys_id, bot_id, utterance, bot_name)
        actual_response.append(response)
    return actual_response
