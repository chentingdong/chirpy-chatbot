import json
import traceback
from datetime import datetime
from urllib.parse import urlencode
import requests
from illusionist.actions.titan import TitanPredict
from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.helpers import order_dict
from python_utils.logger import logger_console, logger
import re


class getBOIncidentStatus(Action):
    """
{
	"api_config": {
		"search_calls":["search_incident","search_workorder"],
		"search_incident": {
			"search_url": "https://bosepoc.cherwellondemand.com/CherwellAPI/api/V1/getsearchresults",
			"search_body": {
				"busObId": "6dd53665c0c24cab86870a21cf6434ae",
				"fieldId": "BO:6dd53665c0c24cab86870a21cf6434ae,FI:6ae282c55e8e4266ae66ffc070c17fa3",
				"filters": [
					{
						"fieldId": "BO:6dd53665c0c24cab86870a21cf6434ae,FI:6ae282c55e8e4266ae66ffc070c17fa3",
						"operator": "contains",
						"value": "search_string"
					},
					{
						"fieldId": "BO:6dd53665c0c24cab86870a21cf6434ae,FI:7605ee2ee7014f6999aa4f9280a9fdf9",
						"operator": "eq",
						"value": "943cce4171beba98e9a6f344dfbfd61c4a73a7acc4"
					}
				],
				"includeAllFields": "false",
				"includeSchema": "false",
				"pageNumber": 1,
				"pageSize": 3,
				"sorting": [
					{
						"fieldId": "BO:6dd53665c0c24cab86870a21cf6434ae,FI:c1e86f31eb2c4c5f8e8615a5189e9b19",
						"sortDirection": -1
					}
				]
			},
			"sorted_by":"Created Date Time",
			"external_url_template": "https://bosepoc.cherwellondemand.com/CherwellPortal/TheServiceHub/SAMLLogin/Command/Queries.GoToRecord?BusObID={busObId}&RecID={busObRecId}",
			"search_results_fields": ["IncidentID", "Description", "Status", "CreatedDateTime"],
			"search_operator_options": ["eq", "gt", "lt", "contains", "startswith"]
		},
		"search_workorder": {
			"search_url": "https://bosepoc.cherwellondemand.com/CherwellAPI/api/V1/getsearchresults",
			"search_body": {
				"busObId": "93e295c50dec612eb13aa5447d8cd839820d7acd1b",
				"fieldId": "BO:93e295c50dec612eb13aa5447d8cd839820d7acd1b,FI:93e295c61785da067d727d43abbc26d5683dc5f840",
				"filters": [
					{
						"fieldId": "BO:93e295c50dec612eb13aa5447d8cd839820d7acd1b,FI:93e295c61785da067d727d43abbc26d5683dc5f840",
						"operator": "contains",
						"value": "search_string"
					},
					{
						"fieldId": "BO:93e295c50dec612eb13aa5447d8cd839820d7acd1b,FI:93e295c50d79058ce15aee4f8a8dfe195652c22f95",
						"operator": "eq",
						"value": "944298f76273d8f2657f93475b9eeef7f369b9b92c"
					}
				],
				"includeAllFields": "true",
				"includeSchema": "false",
				"pageNumber": 1,
				"pageSize": 3,
				"sorting": [
					{
						"fieldId": "BO:93e295c50dec612eb13aa5447d8cd839820d7acd1b,FI:93e295c50d5ef70054478b4b329c4b5bdac51723c9",
						"sortDirection": -1
					}
				]
			},
			"sorted_by":"Created Date Time",
			"external_url_template": "https://bosepoc.cherwellondemand.com/CherwellPortal/TheServiceHub/SAMLLogin/Command/Queries.GoToRecord?BusObID={busObId}&RecID={busObRecId}",
			"search_results_fields": ["WorkOrderID", "CustomerDisplayName", "Title", "Status", "CreatedDateTime"],
			"search_operator_options": ["eq", "gt", "lt", "contains", "startswith"]
		}
	},
	"auth_required": true,
    "version": "1",
    "action_type": "getBOIncidentStatus"
}


    """
    __mapper_args__ = {'polymorphic_identity': 'getBOIncidentStatus'}
    service_name = 'cherwell'

    @logger.exception()
    def run(self, context) -> (str, list):
        results = []
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name).get('params')
        api_config = self.params.get('api_config', '')
        cherwell_incident_id = context.get_local('cherwell_incident_id', '')
        if not cherwell_incident_id:
            cherwell_incident_id = ''

        #----------------- auth to get access_token for the search call
        if service_params:
            auth_resp = get_basic_auth(service_params, context.get_local('auth_resp', ''))

        if auth_resp:
            context.set_local('auth_resp', auth_resp) # set to context so can be reused if not expired
            logger_console.debug('access_token: {access_token}'.format(**auth_resp))

        #---- do search incident base on user input
        #---- added search workOrder too, to use an array of searching calls.
        if auth_resp and api_config:
            #--- get array of search_calls, loop and make call, then merge results
            search_calls = api_config.get('search_calls', [])
            cherwell_userid = api_config.get('cherwell_userid', '')
            cherwell_userid = context.get_local('cherwell_user', {}).get('RecID', '')
            results = []
            for searchCall in search_calls:
                search_config = api_config.get(searchCall, {})
                if search_config and cherwell_userid:
                    results = results + searchCherwell(auth_resp, cherwell_incident_id, search_config, cherwell_userid)

        logger_console.debug('final return of results[]: {}'.format(results))
        code = 'success' if results else 'failure'

        return code, sorted(results, key=lambda i: i['Created Date Time'], reverse=True)


class getCherwellUser(Action):
    """{
          "action_name": "getCherwellUser",
          "action_type": "getCherwellUser",
          "api_config": {
            "search_method": "GET",
            "search_url": "https://bosepoc.cherwellondemand.com/CherwellAPI/api/V3/getuserbyloginid?loginid=search_cherwell_user_id&loginidtype=Internal",
            "search_body": {},
            "skip_search_string": "hi",
            "key_name":"name",
            "search_results_fields": [
              "FullName",
              "FirstName",
              "LastName",
              "RecID"
            ],
            "external_url_template": "no"
          }
        }
    """
    __mapper_args__ = {'polymorphic_identity': 'getCherwellUser'}
    service_name = 'cherwell'

    @logger.exception()
    def run(self, context) -> (str, list):
        results = []
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name).get('params')
        api_config = self.params.get('api_config', '')
        cherwell_user_id = context.get_local('cherwell_user_id', '')

        if not cherwell_user_id:
            return 'failure', results

        #----------------- if user already in context, no need to ask again.
        if context.get_local('cherwell_user', {}).get('RecID', ''):
            return 'success', context.get_local('cherwell_user')

        #----------------- auth to get access_token for the search call
        if service_params:
            auth_resp = get_basic_auth(service_params, context.get_local('auth_resp', ''))

        if auth_resp:
            context.set_local('auth_resp', auth_resp) # set to context so can be reused if not expired
            logger_console.debug('access_token: {access_token}'.format(**auth_resp))

        #---- do search user base on user input userId
        if auth_resp and api_config:
            #--- get array of search_calls, loop and make call, then merge results
            results = []
            search_url = api_config.get('search_url', '').format(**locals())

            # -- only do search if all values available
            if search_url:
                search_url = search_url.replace('search_cherwell_user_id', cherwell_user_id)
                logger_console.debug('searchCherwell for user Info search_url: {}'.format(search_url))
                search_header = {"Accept": "application/json",
                                 'Authorization': 'Bearer ' + auth_resp.get('access_token', '')
                                 }
                logger_console.debug('searchCherwell for user Info search_header: {}'.format(search_header))
                search_response = requests.get(search_url, headers=search_header)
                logger_console.debug('searchCherwell user info research search_response: {}'.format(search_response.json()))
                # -- need to format the cherwell return to KVP for display and external url links
                records = []
                user_fields = search_response.json().get('fields',[])
                if user_fields:
                    records.append(search_response.json())
                    results = format_Cherwell_search_resp(records, api_config)
                if results:
                    context.set_local('cherwell_user', results[0])
                    context.set_local('user_full_name', results[0].get('FullName', results[0].get('FirstName')))
                    context.set_local('user_RecID', results[0].get('FullName', results[0].get('RecID')))


                logger_console.debug('searchCherwell user info research results[]: {}'.format(results))

        logger_console.debug('final return of results[]: {}'.format(results))
        code = 'success' if results else 'failure'

        return code, results



# -------------- shared functions
# -------------- api call to get search results
def searchCherwell(auth_resp, cherwell_incident_id, search_config, cherwell_userid):
    search_url = search_config.get('search_url', '').format(**locals())
    search_body = search_config.get('search_body', '')

    # -- only do search if all values available
    if search_url and search_body:

        filters = search_body.get('filters', [])
        for filter in filters:
            if filter.get('value', '') == 'search_string':
                filter['value'] = cherwell_incident_id
            elif filter.get('value', '') == 'cherwell_userid':
                filter['value'] = cherwell_userid

        search_body['filters'] = filters

        search_header = {'Authorization' : 'Bearer ' + auth_resp.get('access_token', '')}
        # WARNING! -- request trick:
        # #data=search_body is also working, but gives wrong results of unrelated records.
        logger_console.debug('searchCherwell research search_body: {}'.format(search_body))
        search_response = requests.post(search_url, json=search_body, headers=search_header)

        # -- need to format the cherwell return to KVP for display and external url links
        results = format_Cherwell_search_resp(search_response.json().get('businessObjects', []), search_config)

        logger_console.debug('searchCherwell research results[]: {}'.format(results))
    return results

def format_Cherwell_search_resp(records, search_config):
    results = []
    fields_required = search_config.get('search_results_fields', ['Description', 'Status'])
    fields_required.append('external_url')
    key_name = search_config.get('key_name', 'name')
    external_url_template = search_config.get('external_url_template', '')
    for record in records:
        result = {}
        for field in record.get('fields', []):
            if field.get('name') == 'IncidentID':
                result['Incident ID'] = field.get('value')
            elif field.get('displayName') == 'Created Date Time':
                result['Created Date Time'] = datetime.strptime(field.get('value'), "%m/%d/%Y %H:%M:%S %p")
            else:
                result[field.get(key_name)] = field.get('value')

        # external_url
        if external_url_template:
            result['external_url'] = external_url_template.format(**record)

        #filtered_result = {k: v for k, v in result.items() if k in fields_required}
        filtered_result = {}
        for r_field in fields_required:
            filtered_result[r_field] = result.get(r_field, '')

        results.append(filtered_result)

    return results

# -------------- auth call to get access_token for search, token expires in 20 minutes
def get_basic_auth(service_params, auth_resp):
    token_expired = True
    if auth_resp:   # -- check if current auth_resp has already expired
        logger_console.debug( 'auth_resp={}'.format(auth_resp))
        try:
            datetime_expires = datetime.strptime(auth_resp.get('.expires', ''), '%a, %d %b %Y %H:%M:%S GMT')
            datetime_now = datetime.utcnow()
            seconds_before_expired = (datetime_expires - datetime_now).seconds
            logger_console.debug( '(datetime_expires - datetime_now).seconds =  {}'.format(seconds_before_expired))
            if seconds_before_expired > 60:   # consider token expired 60 seconds before .expires defined 20 minutes, in case clock diff.
                token_expired = False
        except ValueError:
            logger_console.debug('.expires from auth resp is not with valid datetime format: {}'.format(datetime.strptime(auth_resp.get('.expires', 'not exists.'))))
    # -- only redo auth if token expired.
    logger_console.debug('token_expired={}'.format(token_expired))
    if token_expired:
        auth_resp = {}
        auth_url = service_params.get('auth_url', '')
        username = service_params.get('username', '')
        password = service_params.get('password', '')
        client_id = service_params.get('client_id', '')
        auth_header = service_params.get('headers_auth', '')
        if auth_url and username and password and client_id and auth_header:  # all 5 fields need to have value to make call
            auth_params = {
                "grant_type": "password",
                "username": username,
                "password": password,
                "client_id": client_id,
                "client_secret": ""
            }
            timeout = service_params.get('timeout', 20)
            auth_response = requests.post(auth_url, headers=auth_header, data=auth_params, timeout=timeout)
            auth_resp = auth_response.json()

    return auth_resp

