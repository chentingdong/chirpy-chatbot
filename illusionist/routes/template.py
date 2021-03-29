
from flask import (jsonify, request, Blueprint)
from illusionist.response import Response
from illusionist.status import Status
from python_utils.flask_sqlalchemy_base import db
from illusionist.routes import routes
from illusionist.models.templates import Template
import simplejson
from python_utils.kafka_handler import KafkaHandler
from python_utils.logger import logger_kafka

@routes.route('/api/1/templates', methods=['POST', 'PUT'])
def upsert_template():
    """
    Upsert a Template.
    ---
    tags:
        - Template
    consumes:
        - application/json
    parameters:
        - name: payloads
          in: body
          required: true—
          schema:
            type: object
            required:
                - name
                - content
            properties:
                name:
                  type: string
                  description: name of the Template
                content:
                  type: string
                  description: template content
    responses:
        500:
            description: error reasoning the question and provide answers
            schema:
                required:
                    - response
                    - reason
                properties:
                    response:
                        type: boolean
                        description: whether the operation was successful. is always false for 400 or 500
                    reason:
                        type: string
                        description: details of the error
        200:
            description: Created Template
            schema:
                required:
                    - response
                    - payloads
                properties:
                    response:
                        type: boolean
                        description: whether the operation was successful. is always true for 200
                    payloads:
                        type: object
    """
    response = Response()
    args = simplejson.loads(request.data, encoding='utf-8')
    name = args.get('name', None)
    if name is None:
        response.failure("no name provided")
        return jsonify(**response.object)
    content = args.get('content', None)
    if content is None:
        response.failure("no content provided")
        return jsonify(**response.object)
    template = Template.query.filter_by(name=name).first() #.order_by(Template.version.desc()).first()
    if template is None:
        template = Template(name=name, content=content)
    else:
        template.name = name
        template.content = content
    db.session.add(template)
    db.session.commit()
    response.session_id = request.args.get('session_id')
    response.add_payload('result', template.to_json())
    response.reason = "Created Template!"
    response.success()
    return jsonify(**response.object)

@routes.route('/api/1/templates')
def get_templates():
    """
    Get all templates
    ---
    tags:
        - template
    produces:
        - application/json
    responses:
        500:
            description: error reasoning the question and provide answers
            schema:
                required:
                    - response
                    - reason
                properties:
                    response:
                        type: boolean
                        description: whether the operation was successful. is always false for 400 or 500
                    reason:
                        type: string
                        description: details of the error
        200:
            description: List of templates
            schema:
                required:
                    - response
                    - payloads
                properties:
                    response:
                        type: boolean
                        description: whether the operation was successful. is always true for 200
                    payloads:
                        type: object

    """
    response = Response()
    search = request.args.get('search', None)
    page = request.args.get('page', 0)
    size = request.args.get('size', 0)

    templates = None
    if search:
        search = '%'+search+'%'
        templates = Template.query.filter(Template.name.like(search))
    else:
        templates = Template.query.order_by(Template.id.desc())
    if size:
        size = int(size)
        templates = templates.limit(size)
    if size and page:
        page = int(page)
        templates = templates.offset(page*size)
    templates = templates.all()
    response.session_id = request.args.get('session_id')
    response.add_payload('result', [i.to_json() for i in templates])
    response.success()

    msg = KafkaHandler.api_request_formatter(request, response)
    logger_kafka.info(msg)

    return jsonify(**response.object)

