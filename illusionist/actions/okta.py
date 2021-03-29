import requests
from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.logger import logger


class OktaCheckUserInGroup(Action):
    """
      "request_url_pattern": "https://{okta_server}/users/{user_id}/groups"
    """
    __mapper_args__ = {'polymorphic_identity': 'OktaCheckUserInGroup'}
    service_name = 'okta'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @logger.exception()
    def run(self, context) -> (str, None):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)

        response = requests.get(self.params.get('request_url_pattern').format(**service_params),
                                headers=service_params.get('headers'),
                                timeout=service_params.get('timeout'))
        if response.status_code == 200:
            groups = [g['id'] for g in response.json()]
            code = 'yes' if service_params['group_id'] in groups else 'no'
        else:
            code = 'no'
        return code, None


class OktaAddUserToGroup(Action):
    """
      request_url_pattern: "https://{okta_server}/groups/{group_id}/users/{user_id}"
      success response: HTTP/1.1 204 No Content
    """
    __mapper_args__ = {'polymorphic_identity': 'OktaAddUserToGroup'}
    service_name = 'okta'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @logger.exception()
    def run(self, context) -> (str, None):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)

        response = requests.put(self.params.get('request_url_pattern').format(**service_params),
                                headers=service_params.get('headers'),
                                timeout=service_params.get('timeout'))
        code = 'success' if response.status_code == 204 else 'failure'
        return code, None
