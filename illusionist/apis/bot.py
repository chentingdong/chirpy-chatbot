from flask import request, jsonify, session, make_response
from python_utils.logger import logger, logger_console
from illusionist.apis.ask import ask, get_context, session_agent_config, set_session_context, build_response, \
    reset_answer
from illusionist.response import Response
from illusionist.status import Status
from illusionist.apis.bp import bp
from illusionist.models.bot import Bot, TestBot
from illusionist.models.agent_bot import AgentBot


@bp.route('/api/1/test_bot/<int:bot_id>/run', methods=['POST'])
@logger.exception()
def test_bot_run(bot_id):
    response = Response()
    request_json = request.json
    agent_id = int(request_json.get('agent_id', 1))
    bot_test = TestBot.query.get(bot_id)
    if not bot_test:
        response.failure("No recorded test data found for this bot.", Status.HTTP_400_BAD_REQUEST)
    else:
        test_data = bot_test.test_set
        response_data = []
        for i, msg in enumerate(test_data):
            if (msg.get('me')):
                logger_console.debug(msg.get('utterance'))
                bot_response = test_data[i + 1]

            # check if next response is of bot
            if bot_response.get('them'):
                request_json["utterance"] = msg.get('message')
                api_response = ask(agent_id, request_json, testing=True)
                logger_console.debug("Ask response: {}".format(api_response))
                case = {
                    "utterance": msg.get('message'),
                    "expectedResponse": bot_response.get('message'),
                    "response": api_response['payloads']['answer']
                }
            else:
                case = {
                    "utterance": msg.get('message'),
                    "expectedResponse": "No bot response found for test data",
                    "response": None
                }
            response_data.append(case)
        response.add_payload("data", response_data)
        response.success()

    session.clear()
    return jsonify(**response.object)


@bp.route('/api/1/ask_bot/<int:bot_id>', methods=['POST'])
@logger.exception()
def ask_bot(bot_id):
    context = get_context()

    # TODO: with clone, there should be only one agent for a bot
    agent_id = AgentBot.query.filter_by(bot_id=bot_id).all()[0].agent_id
    context.set_local('agent_id', agent_id)
    session_agent_config(agent_id)
    set_session_context(request.json, context)

    bot_name = request.json.get('bot_name')
    bot = Bot.query.filter_by(id=bot_id).one_or_none()
    session.setdefault('bots', [bot])
    context.set_local('current_bot', bot_name)
    if not context.get_local('current_node'):
        context.set_local('current_node', 'start')

    response = build_response(context)
    reset_answer(context)
    return jsonify(**response.object)


@bp.route('/api/1/clone_bot/<int:bot_id>', methods=['POST'])
def clone_bot(bot_id):
    try:
        bot = Bot.query.filter_by(id=bot_id).one_or_none()
        bot.clone()
        resp = {'msg': 'Successfully cloned bot {bot.id} from bot {bot_id}'.format(**locals())}
        status = 200
    except Exception as e:
        resp = {'msg': 'Failed to clone bot from {bot_id}, {e} '.format(**locals())}
        status = 400
        logger_console.error(resp['msg'])

    response = make_response(jsonify(**resp), status)
    return response
