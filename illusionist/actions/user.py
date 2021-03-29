from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.logger import logger
import requests
from python_utils.config import server_config
import json


class GetDefaultOrAvailablePrinters(Action):
    __mapper_args__ = {'polymorphic_identity': 'GetDefaultOrAvailablePrinters'}
    service_name = 'user_profile'

    @logger.exception()
    def run(self, context) -> (str, any):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        default_printer = service_params.get('default_printer')
        context.set_local('default_printer', default_printer)
        available_printers = service_params.get('printers')
        code = 'update'
        results = []

        if default_printer != '':
            code = 'available'
        else:
            results = get_user_attributes(available_printers)

        return code, results


class SetDefaultPrinter(Action):
    __mapper_args__ = {'polymorphic_identity': 'SetDefaultPrinter'}
    service_name = 'user_profile'

    @logger.exception()
    def run(self, context) -> (str, None):
        service = Service().find_by_name_and_agent_id(self.service_name, context.get_local('agent_id'))
        default_printer = context.get_local('default_printer')
        if default_printer:

            # Added protocol to server config
            url = server_config.get('configs', {}).get('protocol') + '://' + server_config.get('configs', {}).get(
                'internal_host') + '/api/service/' + str(service.id)

            service.params['default_printer'] = default_printer
            payload = json.dumps(prepare_payload(service))
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            response = requests.put(url, headers=headers, data=payload)
            if response.status_code == 200:
                return 'success', default_printer

        return 'failure', None


class GetUserDetails(Action):
    __mapper_args__ = {'polymorphic_identity': 'GetUserDetails'}
    service_name = 'user_profile'

    @logger.exception()
    def run(self, context):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        result = {'email': service_params.get('email'),
                  'phone_number': service_params.get('phone_number'),
                  'office_building': service_params.get('office_building'),
                  'office_floor': service_params.get('office_floor'),
                  'home_address': service_params.get('home_address')}

        context.set_local('user_email', service_params.get('email'))

        return 'success', result


class GetAssets(Action):
    __mapper_args__ = {'polymorphic_identity': 'GetAssets'}
    service_name = 'user_profile'

    # TODO: To be made generic in future to take a parameter as input and retrieve results
    @logger.exception()
    def run(self, context):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        available_mobiles = service_params.get('assets').get('mobiles')
        return 'success', get_user_attributes(available_mobiles)


def get_user_attributes(user_attributes):
    """Method to iterate over user attributes and prepare list for image-slides template"""
    results = []
    for key, value in user_attributes.items():
        result = {'title': key,
                  'description': value.get('description'),
                  'image_url': value.get('image_url')
                  }
        results.append(result)
    return results


def prepare_payload(service):
    payload = {'name': service.name,
               'version': 1, 'id': service.id,
               'description': service.description,
               'agent_id': service.agent_id,
               'created_on': str(service.created_on),
               'changed_on': str(service.changed_on),
               'params': service.params}

    return payload
