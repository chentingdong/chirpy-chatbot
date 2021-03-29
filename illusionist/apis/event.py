import json
from flask import request, redirect
from python_utils.logger import logger, logger_events
from illusionist.apis.bp import bp


@bp.route('/events', methods=['GET'])
def server_redirect():
    """
    example request:
    http://localhost:3000/events?redirect_url=https:%2F%2Fadidasaspenpreprod.service-now.com%2Fserviceshop%2F%3Fid=sc_cat_item&sys_id=2b69227a37769a005299db9643990ef8&agent_id=45&source_request_id=05ce9774-9838-4e61-9d09-0339200ffb34&event_type=click&event_value=2b69227a37769a005299db9643990ef8
    """
    data = {
        "request_id": request.environ.get("FLASK_REQUEST_ID"),
        "app_id": request.args.get('app_id'),
        "event_type": request.args.get('event_type'),
        "event_value": request.args.get('event_value'),
        "source_request_id": request.args.get('source_request_id')
    }

    logger_events.info(json.dumps(data))

    url = request.args['redirect_url']
    return redirect(url)
