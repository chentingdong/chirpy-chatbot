import re
from google import google
from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.logger import logger


class GoogleSearchOnUtterance(Action):
    __mapper_args__ = {'polymorphic_identity': 'GoogleSearchOnUtterance'}
    service_name = 'google'

    @logger.exception()
    def run(self, context) -> (str, list):
        service_params = Service().get_params(context.get_local('agent_id'), self.service_name)
        number_of_results = service_params.get('number_of_results', 1)
        search_utterance = context.get_local('search_utterance')
        # number_of_results doesn't seem to work in the api, trunc on response.
        response = google.search(search_utterance, number_of_results)
        results = []
        for res in response[:number_of_results]:
            # google api has bug with name field, always append a link, clean it up
            match = re.search('(^.*)http', res.name)
            if match:
                res.name = match.group(1)
            results.append(res.__dict__)
        code = 'success' if results else 'failure'
        return code, results
