from flask import send_from_directory, request, jsonify, url_for, make_response

from illusionist.helpers.util import get_app
from illusionist.servicenow import ServiceNow
from python_utils.logger import logger_console, logger
from illusionist.helpers.nocache import nocache
from illusionist.response import Response
from illusionist.status import Status
from illusionist.apis.bp import bp


@bp.route("/api/1/illusionist/healthcheck", methods=["GET"])
def healthcheck():
    return make_response(jsonify('ok.'), 200)


@bp.route('/docs', defaults={'path': 'index.html'})
@bp.route('/docs/<path:path>')
@nocache
def documentation(path):
    """
    Use Sphinx for automatic document generation from code comments
    :param path: documentation path
    :return: html DOM that serves docs UI on http://<host>/docs
    """
    document_root = 'docs/build/html/'
    return send_from_directory(document_root, path)


@bp.route('/api/1/find_users', methods=['POST'])
@logger.api_access()
def find_users():
    response = Response()

    try:
        args = request.json
        display_name_value = args.get('name_display_value')

    except Exception as e:
        logger_console.error('Failed to retrieve parameters from request: {}, error: {}'.format(e))
        response.failure(reason='failed to retrieve parameters ' + str(e), status=Status.HTTP_400_BAD_REQUEST)
        return jsonify(**response.object)

    sn = ServiceNow()
    users = sn.find_user(display_name_value)
    response.add_payload("on_behalf_of_users", users)
    return jsonify(**response.object)


@bp.route("/site-map")
def site_map():
    app = get_app()
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)