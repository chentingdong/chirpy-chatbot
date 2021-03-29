import json
import traceback
from datetime import datetime
from urllib.parse import urlencode
import requests
from flask import session
from illusionist.actions.titan import TitanPredict
from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.helpers import order_dict
from python_utils.logger import logger_console, logger
from flask_jwt_extended import get_jwt_identity, jwt_required
from illusionist.models.user import User
from flask import request

# TODO: move this to action config.
state_map = {
    "1": "New",
    "2": "In progress",
    "3": "On hold",
    "4": "Resolved",
    "5": "Closed",
    "6": "Canceled"
}


class ServiceNowIncidentsGetStatus(Action):
    """
    action_params = {
        "api_config" : {
            "sysparm_display_value" : "state, number, opened_at, short_description, comments",
            "sysparm_fields" : "state, number, opened_at, short_description, comments",
            "sysparm_limit" : 5,
            "sysparm_query" : "caller_id=javascript:gs.getUserID()^ORDERBYDESCopened_at"
        },
        "display_order" : [
            "state",
            "number",
            "opened_at",
            "short_description",
            "comments"
        ]
    }
    """
    __mapper_args__ = {'polymorphic_identity': 'ServiceNowIncidentsGetStatus'}
    service_name = 'servicenow'

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)

    @logger.exception()
    def run(self, context) -> (str, list):
        domain = context.get_local('luke_answer', {}).get('data', {}).get('domain', 'IT').upper()
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        table = service_params.get('table').get(domain)
        instance_name = context.get_local('instance_name', service_params.get('instance_name'))
        chatbot_user_id = context.get_local('chatbot_user_id', service_params.get('chatbot_user_id'))
        api_config = self.params.get('api_config')
        api_config['sysparm_query'] = api_config.get('sysparm_query').format(**locals())

        table_url_pattern = service_params.get('table_url_pattern').format(**locals())
        config_query = urlencode(api_config)
        url = "{table_url_pattern}?{config_query}".format(**locals())
        auth = (service_params.get('user'), service_params.get('password'))
        headers = service_params.get('headers')
        timeout = service_params.get('timeout')

        response = requests.get(url, auth=auth, headers=headers, timeout=timeout)
        results = response.json().get('result')
        code = 'success' if results else 'failure'

        display_order = self.params.get('display_order')
        results = [order_dict(d, display_order) for d in results]

        for result in results:
            result['state'] = state_map.get(result.get('state', '4'), "Resolved")

        return code, results


class ServiceNowIncidentGetStatusById(Action):
    """
    action_params = {
        "api_config" : {
            "sysparm_fields" : "state, number, opened_at, short_description, comments",
        },
        "display_order" : [
            "state",
            "number",
            "opened_at",
            "short_description",
            "comments"
        ],
        "external_url_template": "https://{instance_name}.service-now.com/nav_to.do?uri=task.do?sysparm_query=number={incident_id}"
    }
    """
    __mapper_args__ = {'polymorphic_identity': 'ServiceNowIncidentGetStatusById'}
    service_name = 'servicenow'
    # Class level default value. To support existing actions without sysparm_query in config
    sysparm_query_config = {
        "IT": {
            "sysparm_fields": "state, number, opened_at, short_description, comments, assignment_group, sys_id",
            "sysparm_query": "caller_id={chatbot_user_id}^ORopened_by={chatbot_user_id}^ORwatch_listLIKE{chatbot_user_id}",
            "display_order": "state, number, opened_at, short_description, assignment_group, comments"
        },
        "HR": {
            "sysparm_fields": "state, number, opened_at, short_description, comments, assignment_group, sys_id",
            "sysparm_query": "opened_for={chatbot_user_id}^ORopened_by={chatbot_user_id}^ORwatch_listLIKE{chatbot_user_id}",
            "display_order": "state, number, opened_at, short_description, assignment_group, comments"
        },
        "FINANCE": {
            "sysparm_fields": "state, number, opened_at, short_description, comments, assignment_group, sys_id",
            "sysparm_query": "caller={chatbot_user_id}^ORopened_by={chatbot_user_id}^ORwatch_listLIKE{chatbot_user_id}",
            "display_order": "state, number, opened_at, short_description, assignment_group, comments"
        }
    }
    ticket_match = 'LIKE'

    @logger.exception()
    def fetch(self, context):
        domain = context.get_local('luke_answer', {}).get('data', {}).get('domain', 'IT').upper()
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        incident_id = context.get_local('servicenow_incident_id')
        chatbot_user_id = context.get_local('chatbot_user_id', service_params.get('chatbot_user_id'))
        # Preference: service level config -> action level config
        api_config = service_params.get('api_config', self.params.get('api_config'))

        # Fallback to class level default incase config not available at action level
        # in case sysparm_query in action config has only for one domain use class level default for others
        query = api_config.get('sysparm_query_config', self.sysparm_query_config).get(domain, self.sysparm_query_config.get(domain)).get('sysparm_query')
        query += '^number' + api_config.get('ticket_match', self.ticket_match) + incident_id
        query = query.format(**locals())
        api_config['sysparm_query'] = query

        # set sysparm_fields
        api_config['sysparm_fields'] = api_config.get('sysparm_query_config', self.sysparm_query_config).get(domain, self.sysparm_query_config.get(domain)).get('sysparm_fields')

        table = service_params.get('table').get(domain)
        instance_name = context.get_local('instance_name', service_params.get('instance_name'))
        table_url_pattern = service_params.get('table_url_pattern').format(**locals())
        config_query = urlencode(api_config)

        url = "{table_url_pattern}?{config_query}&sysparm_display_value=true".format(**locals())
        auth = (service_params.get('user'), service_params.get('password'))
        headers = service_params.get('headers')
        timeout = service_params.get('timeout')

        service_now_response = requests.get(url, auth=auth, headers=headers, timeout=timeout)
        results = service_now_response.json().get('result', [])

        for result in results:
            # To return display_value instead of reference.
            for key, value in result.items():
                if type(value) is dict and value['display_value']:
                    result[key] = result[key]['display_value']

        # rearranging as per display order
        display_order = api_config.get('sysparm_query_config', self.sysparm_query_config).get(domain, self.sysparm_query_config.get(domain)).get('display_order')
        results = [order_dict(d, display_order) for d in results]
        return results

    @logger.exception()
    def run(self, context) -> (str, list):
        results = self.fetch(context)
        code = 'success' if results else 'failure'
        return code, results


class ServiceNowIncidentsGetStatusClickMessage(Action):
    """
    self.params = {
        "title_field" : "number"
    }
    """
    __mapper_args__ = {'polymorphic_identity': 'ServiceNowIncidentsGetStatusClickMessage'}
    service_name = 'servicenow'

    @logger.exception()
    def run(self, context) -> (str, list):
        results = ServiceNowIncidentsGetStatus.query.first().run(context)
        code = 'success' if results else 'failure'

        for result in results:
            title_field = self.params.get('title_field', 'title')
            result['message'] = result.get(title_field, '')

        return code, results


class ServiceNowIncidentsGetStatusLinkOut(Action):
    """
    self.params = {
        "external_url_template" : "https://{instance_name}.service-now.com/nav_to.do?uri=task.do?sysparm_query=number={number}"
    }
    """
    __mapper_args__ = {'polymorphic_identity': 'ServiceNowIncidentsGetStatusLinkOut'}
    service_name = 'servicenow'

    @logger.exception()
    def run(self, context) -> (str, list):
        code, results = ServiceNowIncidentsGetStatus.query.one_or_none().run(context)

        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        instance_name = context.get_local('instance_name', service_params.get('instance_name'))
        for result in results:
            number = result.get('number')
            result['external_url'] = self.params.get('external_url_template').format(**locals())
        code = 'success'

        return code, results


class ServiceNowIncidentCreate(Action):
    """
    service_params = {
        "base_url" : "service-now.com",
        "entity_url_pattern" : {
            "FIN" : "https://{instance_name}.service-now.com/kb_knowledge.do?sys_id={sys_id}",
            "hr" : "https://{instance_name}.service-now.com/kb_knowledge.do?sys_id={sys_id}",
            "it" : "https://{instance_name}.service-now.com/sp?id=kb_article&sys_id={sys_id}"
        },
        "finance_table" : "finance",
        "form_view_url_path" : "sp?id=sc_cat_item&sys_id=",
        "headers" : {
            "Accept" : "application/json",
            "Content-Type" : "application/json"
        },
        "instance_name" : "ven01701",
        "my_request_url" : "https://{instance_name}.service-now.com/sp?id=requests",
        "password" : "Astound2018",
        "sys_user_table" : "servicenow.adidasaspen_sys_user",
        "table" : {
            "FIN" : "finance",
            "hr" : "hr_case",
            "it" : "incident"
        },
        "timeout" : 10,
        "user" : "admin"
    }
    """
    __mapper_args__ = {'polymorphic_identity': 'ServiceNowIncidentCreate'}
    service_name = 'servicenow'

    @logger.exception()
    def run(self, context) -> (str, dict):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        titan = TitanPredict.query.first()
        categories = {}
        assignment_groups = {}

        if service_params.get('predict_categories', True):
            categories = titan.predict_categories(context)

        if service_params.get('predict_assignment_groups', True):
            assignment_groups = titan.predict_assignment_group(context)

        try:
            data = self.create_ticket(context, categories=categories, assignment_groups=assignment_groups)
            code = 'success'
        except Exception as e:
            logger_console.error('Failed creating ticket: {}'.format(e))
            logger_console.warning(traceback.format_exc())
            data = {}
            code = 'failure'

        return code, data

    def create_ticket(self, context, categories=None, assignment_groups=None):
        if not categories:
            categories = {}
        if not assignment_groups:
            assignment_groups = {}

        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        urgency_map = service_params.get('urgency_map', {})
        domain = context.get_local('luke_answer', {}).get('data', {}).get('domain', 'IT').upper()
        on_behalf_of_user = context.get_local('on_behalf_of_user')
        caller_id, u_announcer = self.get_on_behalf_of(context)

        default_fields = self.params.get('default_fields').get(domain, {})
        context_fields = {
            'caller_id': caller_id,
            'opened_by': service_params.get('virtual_agent_user_id', context.get_local('virtual_agent_user_id')),
            'country': service_params.get('country', context.get_local('country')),
            'u_announcer': u_announcer,
            'u_requested_on_behalf': context.get_local('u_requested_on_behalf'),
            'u_opened_by_group': context.get_local('group'),
            'short_description': context.get_local('short_description'),
            'description': context.get_local('description'),
            'instance_name': context.get_local('instance_name', service_params.get('instance_name')),
            'urgency': urgency_map.get(context.get_local('urgency'), 1),
            'u_ticket_type': 'inc',
            'u_department': context.get_local('domain', 'IT')
        }
        combined_fields = {**default_fields, **context_fields, **categories, **assignment_groups}

        data = json.dumps(combined_fields)
        headers = service_params.get('headers')
        user = service_params.get('user')
        password = service_params.get('password')
        auth = (user, password)

        table = service_params.get('table').get(domain)
        instance_name = context.get_local('instance_name', service_params.get('instance_name'))
        url = service_params.get('table_url_pattern').format(**locals())

        logger_console.info('request. url: {}, data: {}'.format(url, data))
        response = requests.post(url=url, auth=auth, headers=headers, data=data)
        if response.status_code == 201:
            data = response.json()
        else:
            data = {'Status, {}, Headers: {}, Error: {}'.format(response.status_code, response.headers, response.content)}
        logger_console.info('response. data: {}, status_code: {}, text: {}'.format(data, response.status_code, response.text))
        sys_id = data.get('result').get('sys_id')
        ticket_number = data.get('result').get('number')
        entity_view_url = service_params.get('entity_view_url_pattern').get(domain).format(**locals())
        entity_edit_url = service_params.get('entity_edit_url_pattern').get(domain).format(**locals())

        result = {
            'view_url': entity_view_url,
            'edit_url': entity_edit_url,
            'ticket_number': ticket_number
        }

        # To use in email content after ticket creation
        context.set_local('view_url', entity_view_url)

        return result

    def get_on_behalf_of(self, context):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        on_behalf_of_user = context.get_local('on_behalf_of_user')
        if on_behalf_of_user:
            caller_id = on_behalf_of_user
            u_announcer = context.get_local('chatbot_user_id', service_params.get('chatbot_user_id'))
        else:
            caller_id = service_params.get('chatbot_user_id', context.get_local('chatbot_user_id'))
            u_announcer = ''

        return caller_id, u_announcer


class ServiceNowIncidentUpdate(Action):
    """
    service_params{
        "base_url": "service-now.com",
        "entity_url_pattern": {
            "FINANCE": "https://{instance_name}.service-now.com/kb_knowledge.do?sys_id={sys_id}",
            "hr": "https://{instance_name}.service-now.com/kb_knowledge.do?sys_id={sys_id}",
            "it": "https://{instance_name}.service-now.com/sp?id=kb_article&sys_id={sys_id}"
        },
        "finance_table": "finance",
        "form_view_url_path": "sp?id=sc_cat_item&sys_id=",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "instance_name": "ven01701",
        "my_request_url": "https://{instance_name}.service-now.com/sp?id=requests",
        "password": "Astound2018",
        "sys_user_table": "servicenow.adidasaspen_sys_user",
        "tables": {
            "FINANCE": "finance",
            "hr": "hr_case",
            "it": "incident"
        },
        "timeout": 10,
        "user": "admin"
    }
    """

    __mapper_args__ = {'polymorphic_identity': 'ServiceNowIncidentUpdate'}
    service_name = 'servicenow'

    def get_sys_id(self, context) -> str:
        results = ServiceNowIncidentGetStatusById.query.first().fetch(context)
        sys_id = results[0]['sys_id']
        return sys_id

    @logger.exception()
    def run(self, context) -> (str, list):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        instance_name = context.get_local('instance_name', service_params.get('instance_name'))

        sys_id = self.get_sys_id(context)
        url = self.params['update_url_pattern'].format(sys_id=sys_id, **service_params)
        auth = (service_params.get('user'), service_params.get('password'))
        headers = service_params.get('headers')
        data = json.dumps({"comment": context.get_local('comment')})
        timeout = service_params.get('timeout', 60)

        code = 'failure'
        results = []
        try:
            response = requests.put(url, auth=auth, headers=headers, data=data, timeout=timeout)
            domain = context.get_local('luke_answer', {}).get('data', {}).get('domain', 'it')
            table = service_params.get('table').get(domain)
            if response.status_code != 200:
                logger_console.error('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
            else:
                domain = context.get_local('luke_answer', {}).get('data', {}).get('domain')
                incident_id = context.get_local('servicenow_incident_id', 'link')
                entity_view_url = service_params.get('entity_view_url_pattern').get(domain).format(**locals())
                entity_edit_url = service_params.get('entity_edit_url_pattern').get(domain).format(**locals())
                results = [{
                    'title': 'View ticket {}'.format(incident_id),
                    'url': entity_view_url
                }, {
                    'title': 'Edit ticket {} (may need permission)'.format(incident_id),
                    'url': entity_edit_url
                }]
                code = 'success'
        except Exception as e:
            logger_console.error(e)

        return code, results


class ServiceNowSearchUser(Action):
    __mapper_args__ = {'polymorphic_identity': 'ServiceNowSearchUser'}
    service_name = 'servicenow'

    @logger.exception()
    def run(self, context) -> (str, list):
        name_email = context.get_local('name_email')
        name_email = ' '.join(name_email.split()).lower()
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        sys_user_table = service_params.get('sys_user_table')
        instance_name = context.get_local('instance_name', service_params.get('instance_name'))
        auth = (service_params.get('user'), service_params.get('password'))
        headers = service_params.get('headers')
        url = service_params.get('table_url_pattern').format(instance_name=instance_name, table=sys_user_table)
        timeout = service_params.get('timeout', 60)

        api_config = self.params.get('api_config')
        api_config['sysparm_query'] = 'user_nameLIKE' + name_email + '^ORemailLIKE' + name_email + '^ANDuser_name!=""'

        config_query = urlencode(self.params.get('api_config'))
        url = url + '?{}'.format(config_query)

        code = 'failure'
        users = []
        try:
            response = requests.get(url, auth=auth, headers=headers, timeout=timeout)
            if response.status_code == 200:
                result = response.json().get('result')
                users = [user.get('name') for user in result]
                code = 'success'
            else:
                logger_console.error('Status: {} '.format(response.status_code))
        except Exception as e:
            logger_console.error(e)

        return code, users


class ServiceNowGetUserById(Action):
    __mapper_args__ = {'polymorphic_identity': 'ServiceNowGetUserById'}
    service_name = 'servicenow'

    @jwt_required
    @logger.exception()
    def run(self, context) -> (str, list):
        #ToDo Temporary work around added for McD demo. In future will get user_id from widget
        user = User.query.filter_by(username=get_jwt_identity()).one_or_none()
        servicenow_user_id = user.profile.get('servicenow_user')
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        sys_user_table = service_params.get('sys_user_table')
        instance_name = service_params.get('instance_name')
        auth = (service_params.get('user'), service_params.get('password'))
        headers = service_params.get('headers')
        url = service_params.get('table_url_pattern').format(instance_name=instance_name, table=sys_user_table)
        url = '{}/{}?sysparm_display_value=true'.format(url, servicenow_user_id)
        timeout = service_params.get('timeout', 60)

        code = 'failure'
        user_info = {}
        try:
            response = requests.get(url, auth=auth, headers=headers, timeout=timeout)
            if response.status_code == 200:
                user_info = response.json().get('result')
                context.set_local('servicenow_user_info', user_info)
                code = 'success'
            else:
                logger_console.error('Status: {} '.format(response.status_code))
        except Exception as e:
            logger_console.error(e)

        return code, user_info

