import json
import requests
from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.logger import logger


class TitanPredict(Action):
    """
    service_params = {
        "model_id": {
            "category": {
                "it": 121,
                "hr": 0,
                "fin": 123
            },
            "assignment_group": {
                "it": 89,
                "hr": 87,
                "fin": 88
            }
        }
        "base_url": "https://titan-api-dev.astound.ai"
    }
    """
    __mapper_args__ = {'polymorphic_identity': 'TitanPredict'}
    service_name = 'titan'

    def run(self):
        pass

    @logger.exception()
    def predict(self, predict_type, context) -> dict:
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        domain = context.get_local('luke_answer', {}).get('data', {}).get('domain', 'IT')
        model_id = service_params[predict_type].get(domain)
        url = service_params['url_pattern'].format(**locals())
        headers = {
            'x-consumer-custom-id': str(context.get_local('org_id')),
            'Upstream-Request_Id': context.get_local('request_id'),
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
        # TODO: confirm titan predict api schema
        data = json.dumps({
            'query': context.get_local('short_description', '') + '. ' + context.get_local('description', ''),
            'short_description': context.get_local('short_description', '') + '. ' + context.get_local('description', ''),
            'country': context.get_local('country'),
            'company': context.get_local('company')
        })
        response = requests.post(url=url, headers=headers, data=data)
        result = response.json()

        return result

    @logger.exception()
    def predict_categories(self, context) -> dict:
        """
        it:
        predict =  {
            "category": "*",
            "id": "d789a11e-b4d6-55bb-b18d-0859fa13af7a",
            "precision": 0.6766341328620911,
            "rank": 1,
            "service": "Microstrategy",
            "source": "ServiceNow",
            "subservice": "Platform",
            "triad": "Microstrategy|Platform|*"
        }
        hr: none
        fin:
        predict = {
            "cat_lvl_1": "Travel",
            "cat_lvl_1_id": "a9049119375b56007ed28f0843990ead",
            "cat_lvl_2": "User/Profile",
            "cat_lvl_2_id": "e9049119375b56007ed28f0843990ead",
            "cat_lvl_3": "User Issue / Creation",
            "cat_lvl_3_id": "2d049119375b56007ed28f0843990ead",
            "id": "37546899-11ec-5ee8-a3a3-84304796345e",
            "levels": "Travel|User/Profile|User Issue / Creation",
            "precision": 0.999956488609314,
            "rank": 1,
            "source": "ServiceNow"
        }
        """

        predict = self.predict('category', context)['results'][0]
        if not predict:
            return {}

        domain = context.get_local('luke_answer', {}).get('data', {}).get('domain', 'IT').upper()
        if domain.upper() == 'IT':
            categories = {
                'u_category': predict.get('category', None),
                'u_service': predict.get('service', None),
                'u_subservice': predict.get('subcategory', None)
            }
        elif domain.upper() == 'FINANCE':
            categories = {
                "u_category_level_1": predict.get('cat_lvl_1', None),
                "u_category_level_2": predict.get('cat_lvl_2', None),
                "u_category_level_3": predict.get('cat_lvl_3', None)
            }
        else:
            categories = {}

        return categories

    @logger.exception()
    def predict_assignment_group(self, context) -> dict:
        """
        same response schema for it, hr, fin
        predict = {
            "ag_name": "GLBL_MICROSTRATEGY_EXT",
            "id": "9c2831d3-21d3-5cee-9097-8a3ec4256d4a",
            "precision": 0.9237868189811707,
            "rank": 1,
            "source": "ServiceNow"
        }
        """
        predict = self.predict('assignment_group', context)['results']
        if predict:
            assignment_groups = {'assignment_group': predict[0]['assignment_group']}
        else:
            assignment_groups = {'assignment_group': ''}
        return assignment_groups
