import json
import requests
from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.logger import logger_console, logger


class LukeGetInfo(Action):
    __mapper_args__ = {'polymorphic_identity': 'LukeGetInfo'}
    service_name = 'luke'

    @logger.exception()
    def run(self, context) -> (str, list):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        url = service_params.get('search_url')
        timeout = service_params.get('timeout', 60)
        headers = service_params.get('headers')
        data = json.dumps({
            "utterance_obj": {
                "utterance": context.get_local('utterance'),
                "domain": context.get_local('luke_answer', {}).get('data', {}).get('domain', 'it')
            },
            "country": context.get_local('country')
        })

        try:
            response = requests.post(url, data=data, headers=headers, timeout=timeout)
            answers = response.json().get('answer', [])

            # TODO: rewrite luke component to return url, use document_id as placeholder for now
            results = [{"title": answer['title'], "url": answer['document_id']} for answer in answers]
            code = 'success'
        except Exception as e:
            logger_console.error(e)
            results = []
            code = 'failure'

        return code, results


class CheckDomain(Action):
    __mapper_args__ = {'polymorphic_identity': 'CheckDomain'}

    @logger.exception()
    def run(self, context) -> (str, None):
        domain = context.get_local('luke_answer', {}).get('data', {}).get('domain').lower()
        return domain, None


class LukeGetKB(Action):
    """{
            "config": {
                "agent_id": 16,
                "kb_agent_id": 16,
                "form_agent_id": 17,
                  "no_kb_then_search_form":true,
                "document_view_url": "https://bosepoc.cherwellondemand.com/CherwellPortal/TheServiceHub/SAMLLogin/Command/Queries.GoToRecord?BusObID=93fdad44c17219af320e804d2ba32b5101140e903e&RecID={}"
            }
        }    """
    __mapper_args__ = {'polymorphic_identity': 'LukeGetKB'}
    service_name = 'luke'

    @logger.exception()
    def run(self, context) -> (str, list):
        agent_config = self.params.get('config', '')
        code, results = call_luke(context, agent_config, self.service_name)
        # check if no_kb_then_search_form is true to search form
        no_kb_then_search_form = agent_config.get('no_kb_then_search_form', True)
        if code == 'success':
            code = 'have_kb'
        else:
            agent_config['agent_id'] = agent_config.get('form_agent_id', '')
            agent_config['document_view_url'] = agent_config.get('form_document_view_url', '')
            code, results = call_luke(context, agent_config)
            if code == 'success':
                code = 'have_form'

        # code should be have_kb, have_form, failure
        return code, results



class LukeGetForm(Action):
    """
        "action_params": {
                "config": {
                    "agent_id": 17,
                    "document_view_url": "https://bosepoc.cherwellondemand.com/CherwellPortal/TheServiceHub/SAMLLogin/Command/Queries.GoToRecord?BusObID=934986ba1e6ea051a9def5461fbe8d4434cd5c3b45&RecID={}"
                },
            "version": "1",
            "action_type": "LukeGetForm"
        }
        """
    __mapper_args__ = {'polymorphic_identity': 'LukeGetForm'}
    service_name = 'luke'

    @logger.exception()
    def run(self, context) -> (str, list):
        agent_config = self.params.get('config', '')

        code, results = call_luke(context, agent_config, self.service_name)
        if code == 'success':
            code = 'have_form'

        # code should be have_form, failure
        return code, results


def call_luke(context, config, service_name):
    service_params = Service().get_params(context.get_local('agent_id'), service_name)
    """
    answer_url : {luke_host}/api/agents/{agent_id}/answer
    
    document_view_url 
    subcategories: https://bosepoc.cherwellondemand.com/CherwellPortal/TheServiceHub/SAMLLogin/Command/Queries.GoToRecord?BusObID=934986ba1e6ea051a9def5461fbe8d4434cd5c3b45&RecID={rec_id}
    ckcs: https://bosepoc.cherwellondemand.com/CherwellPortal/TheServiceHub/SAMLLogin/Command/Queries.GoToRecord?BusObID=93fdad44c17219af320e804d2ba32b5101140e903e&RecID={rec_id}
    """

    code = 'failure'
    results = []

    agent_id = config.get('agent_id', '')
    return_limit = config.get('return_limit', 5)
    url = service_params.get('answer_url', '').format(agent_id)
    document_view_url = config.get('document_view_url', '')

    # do not make any call if cannot get url, agent_id and document_view_url
    if agent_id and url and document_view_url:
        timeout = service_params.get('timeout', 60)
        headers = service_params.get('headers', {"Content-Type": "application/json"})
        data = json.dumps({
            "utterance": context.get_local('search_string','no search_string'),
            "session_context": {
                "country": context.get_local('country', 'US'),
                "return_full_ir": False
            }
        })

        try:
            response = requests.post(url, data=data, headers=headers, timeout=timeout)

            # ToDo check response code
            luke_response = response.json()
            context.set_local('luke_answer', luke_response)
            answers = luke_response.get('data', {})
            logger_console.debug("call_luke action response answers: {}".format(answers))

            if "info" in answers:
                documents = answers.get('info', [])[:return_limit]  # temp set limited return here, should be set by the luke end
                results = [{"title": document.get('title', 'No Title'),
                            "description": document.get('description', 'No Description'),
                            "url": document_view_url.format(document['display_info']['ext_doc_id'])} for document in
                           documents]
            if results:
                code = 'success'

        except Exception as e:
            logger_console.error(e)

    return code, results
