import traceback

from flask import request, jsonify, make_response
from illusionist.models.agent import AgentsSimilarityMatrix
from python_utils.logger import logger, logger_console
from illusionist.apis.bp import bp


@bp.route('/api/agents_similarity_matrix/update', methods=['POST'])
@logger.exception()
def update_similarity_matrix():
    nlps = ['spacy']
    match_units = ['list']

    try:
        status = 200
        request_json = request.json
        agent_id = request_json['agent_id']
        nlps = request_json.get('nlps', nlps)
        match_units = request_json.get('match_units', match_units)

        for nlp in nlps:
            for match_unit in match_units:
                AgentsSimilarityMatrix(agent_id).update(nlp=nlp, match_unit=match_unit)
        resp = {'msg': 'success to built similarity matrix.'}
    except Exception as e:
        logger_console.warning(traceback.format_exc())
        status = 400
        resp = {'error': e}

    return make_response(jsonify(**resp), status)


@bp.route('/api/agents_similarity_matrix/<int:agent_id>/<string:nlp>/<string:match_unit>', methods=['GET'])
@logger.exception()
def get_similarity_matrix(agent_id, nlp, match_unit):
    matrix = AgentsSimilarityMatrix.query.filter_by(agent_id=agent_id, nlp=nlp, match_unit=match_unit).one_or_none()
    try:
        status = 200
        resp = {'matrix': matrix.matrix}
    except Exception as e:
        logger_console.warning(traceback.format_exc())
        status = 400
        resp = {'error': e}

    return make_response(jsonify(**resp), status)