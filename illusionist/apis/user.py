from flask import request, jsonify, make_response
from flask_bcrypt import Bcrypt
from illusionist.response import Response
from illusionist.status import Status
from illusionist.models.user import User
from python_utils.flask_sqlalchemy_base import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from illusionist.apis.bp import bp

jwt = JWTManager()
bcrypt = Bcrypt()


# TODO: move this to a seperate api file.
@bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'roles': [ur.role.name for ur in user.user_role]
    }


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


@bp.route('/users/login', methods=['POST'])
def authenticate():
    response = Response()
    bcrypt.check_password_hash
    username = request.json.get('username')
    password = request.json.get('password')
    if username and password:
        user = User.query.filter_by(username=username).one_or_none()

        if user is None:
            response.failure("Username doesn't exist.", Status.HTTP_401_UNAUTHORIZED)
        else:
            if bcrypt.check_password_hash(user.password, password):
                response.add_payload('access_token', create_access_token(identity=user))
                response.success()
            else:
                response.failure('Invalid password.', Status.HTTP_401_UNAUTHORIZED)
    else:
        response.failure("username or password wrong.", Status.HTTP_401_UNAUTHORIZED)
    return make_response(jsonify(**response.object), response.status)


@bp.route('/users/signup', methods=['POST'])
def register():
    response = Response()
    payload = request.get_json()
    username = payload.get('username')
    password = payload.get('password')
    role = request.json.get('role')
    if username and password:
        user = User.query.filter_by(username=username).one_or_none()
        if user is not None:
            response.failure('Username already exists.', Status.HTTP_400_BAD_REQUEST)
        else:
            user = User(username=username, password=bcrypt.generate_password_hash(password, 10),
                        first_name=payload.get('first_name'), last_name=payload.get('last_name'))
            if role:
                user.roles.append(role)
            db.session.add(user)
            db.session.commit()
            response.success()
    else:
        response.failure("username or password invalid", Status.HTTP_400_BAD_REQUEST)
    return make_response(jsonify(**response.object), response.status)


@bp.route('/users/me', methods=['GET'])
@jwt_required
def me():
    response = Response()
    user = User.query.filter_by(username=get_jwt_identity()).one_or_none()
    if user is None:
        response.failure('Invalid token', Status.HTTP_401_UNAUTHORIZED)
    else:
        response.add_payload('data', user.get_info())
        response.success()
    return make_response(jsonify(**response.object), response.status)

