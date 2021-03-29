#
# from flask import (jsonify, request, Blueprint)
# from illusionist.response import Response
# from illusionist.status import Status
# from illusionist.routes import routes
# from illusionist.models.workflows import Workflow
# import simplejson
#
#
# @routes.route('/api/1/workflows', methods=['POST', 'PUT'])
# def upsert_workflow():
#     """
#     Upsert a Workflow.
#     ---
#     tags:
#         - Workflow
#     consumes:
#         - application/json
#     parameters:
#         - name: payloads
#           in: body
#           required: true
#           schema:
#             type: object
#             required:
#                 - name
#                 - content
#             properties:
#                 name:
#                   type: string
#                   description: name of the Workflow
#                 content:
#                   type: string
#                   description: xml content as string
#     responses:
#         500:
#             description: error reasoning the question and provide answers
#             schema:
#                 required:
#                     - response
#                     - reason
#                 properties:
#                     response:
#                         type: boolean
#                         description: whether the operation was successful. is always false for 400 or 500
#                     reason:
#                         type: string
#                         description: details of the error
#         200:
#             description: Created Workflow
#             schema:
#                 required:
#                     - response
#                     - payloads
#                 properties:
#                     response:
#                         type: boolean
#                         description: whether the operation was successful. is always true for 200
#                     payloads:
#                         type: object
#     """
#     response = Response()
#     args = simplejson.loads(request.data, encoding='utf-8')
#     name = args.get('name', None)
#     if name is None:
#         response.failure("no name provided")
#         return jsonify(**response.object), Status.HTTP_400_BAD_REQUEST
#     xml = request.args.get('content', None)
#     if xml is None:
#         response.failure("no xml provided")
#         return jsonify(**response.object)
#     workflow = Workflow.query.filter_by(name=name).order_by(Workflow.version.desc()).first()
#     version = 1
#     if workflow is not None:
#         version = workflow.version + 1
#     workflow = Workflow(name, xml, version)
#     db.session.add(workflow)
#     db.session.commit()
#     response.session_id = request.args.get('session_id')
#     response.add_payload('result', workflow.to_json(False))
#     response.reason = "Created workflow!"
#     response.success()
#     return jsonify(**response.object), Status.HTTP_201_CREATED
#
#
# @routes.route('/api/1/workflows/<int:workflow_id>')
# def open_workflow(workflow_id):
#     """
#     Open A Workflow
#     ---
#     tags:
#         - Workflow
#     produces:
#         - application/json
#     parameters:
#         - name: workflow_id
#           type: int
#           in: path
#           required: true
#     responses:
#         500:
#             description: error reasoning the question and provide answers
#             schema:
#                 required:
#                     - response
#                     - reason
#                 properties:
#                     response:
#                         type: boolean
#                         description: whether the operation was successful. is always false for 400 or 500
#                     reason:
#                         type: string
#                         description: details of the error
#         200:
#             description: Open a workflow
#             schema:
#                 required:
#                     - response
#                     - payloads
#                 properties:
#                     response:
#                         type: boolean
#                         description: whether the operation was successful. is always true for 200
#                     payloads:
#                         type: object
#
#     """
#     response = Response()
#     workflow = Workflow.query.get(workflow_id)
#     if not workflow:
#         response.failure()
#         response.reason = 'Workflow not found!'
#         response.session_id = 1
#         return jsonify(**response.object), Status.HTTP_400_BAD_REQUEST
#     response.session_id = request.args.get('session_id')
#     response.add_payload('result', workflow.to_json())
#     response.reason = 'Found workflow'
#     response.success()
#     return jsonify(**response.object), Status.HTTP_200_OK
#
#
# @routes.route('/api/1/workflows')
# def get_workflows():
#     """
#     Get all workflows
#     ---
#     tags:
#         - Workflow
#     produces:
#         - application/json
#     responses:
#         500:
#             description: error reasoning the question and provide answers
#             schema:
#                 required:
#                     - response
#                     - reason
#                 properties:
#                     response:
#                         type: boolean
#                         description: whether the operation was successful. is always false for 400 or 500
#                     reason:
#                         type: string
#                         description: details of the error
#         200:
#             description: List of Workflows
#             schema:
#                 required:
#                     - response
#                     - payloads
#                 properties:
#                     response:
#                         type: boolean
#                         description: whether the operation was successful. is always true for 200
#                     payloads:
#                         type: object
#
#     """
#     response = Response()
#     search = request.args.get('search', None)
#     page = request.args.get('page', 0)
#     size = request.args.get('size', 0)
#
#     workflows = None
#     if search:
#         search = '%'+search+'%'
#         workflows = Workflow.query.filter(Workflow.name.like(search))
#     else:
#         workflows = Workflow.query.order_by(Workflow.id.desc())
#     if size:
#         size = int(size)
#         workflows = workflows.limit(size)
#     if size and page:
#         page = int(page)
#         workflows = workflows.offset(page*size)
#     workflows = workflows.all()
#     response.session_id = request.args.get('session_id')
#     response.add_payload('result', [i.to_json(False) for i in workflows])
#     response.success()
#     return jsonify(**response.object), Status.HTTP_200_OK
#
