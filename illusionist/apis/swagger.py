from flask import jsonify
from flask_swagger import swagger
from illusionist.helpers.reverse_proxied import ReverseProxied
from illusionist.apis.bp import bp


@bp.route("/flasgger")
def spec():
    """
    This endpoint serves swagger api. Swagger UI are managed in another service managed by docker-compose
    :return:
    """
    from illusionist.helpers.util import get_app
    app = get_app()
    # Use flasgger to extract OpenAPI=Specification from all Flask views registered in this app.
    app.config['SWAGGER'] = {
        "swagger_version": 2
    }

    app.wsgi_app = ReverseProxied(app.wsgi_app, '/illusionist')

    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Illusionist Swagger API"
    return jsonify(swag)