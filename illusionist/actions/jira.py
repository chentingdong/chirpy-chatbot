import json
import requests
from jira import JIRA
from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.logger import logger_console, logger


class JiraServiceDeskCreateTicket(Action):
    """not deployed to any bot, no service settings"""
    __mapper_args__ = {'polymorphic_identity': 'JiraServiceDeskCreateTicket'}
    service_name = 'jira'

    @logger.exception()
    def run(self, context) -> (str, dict):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        service_url = service_params['service_url']
        user = service_params.get('user')
        password = service_params.get('password')
        jira = JIRA(service_url, auth=(user, password))
        summary = service_params['subject_pattern'].format(**context.local_variables)
        description = context.get_local('description')
        project = service_params['project']
        issue_type = service_params['issue_type']

        new_issue = jira.create_issue(project=project, issuetype=issue_type, summary=summary, description=description)
        data = {'url': new_issue.permalink()}
        code = 'success'
        return code, data


class JiraCoreCreateTicket(Action):
    __mapper_args__ = {'polymorphic_identity': 'JiraCoreCreateTicket'}
    service_name = 'jira'

    @logger.exception()
    def run(self, context) -> (str, dict):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)

        url = service_params['service_url']
        user = service_params.get('user')
        password = service_params.get('password')
        auth = (user, password)
        headers = self.params.get('headers')
        fields = service_params.get('fields')
        fields['summary'] = context.get_local('short_description', 'Create a ticket')
        fields['description'] = context.get_local('description')
        payload = json.dumps({"fields": fields})

        code = "failure"
        data = {}
        logger_console.info('jira create ticket payload, {}'.format(payload))
        response = requests.post(url=url, auth=auth, headers=headers, data=payload)
        logger_console.info('response, {}'.format(response.status_code))
        if response.status_code == 201:
            ticket_key = response.json().get('key')
            data = {
                'url': self.params.get('ticket_url_pattern').format(ticket_key=ticket_key)
            }
            code = "success"

        return code, data
