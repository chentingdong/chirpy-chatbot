from flask import Blueprint
routes = Blueprint('routes', __name__)

from illusionist.routes.workflow import *
from illusionist.routes.template import *
