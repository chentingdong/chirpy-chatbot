import json
import requests
from illusionist.models.service import Service

from illusionist.models.action import Action
from python_utils.logger import logger


class SearchJenkinsJob(Action):
    __mapper_args__ = {'polymorphic_identity': 'SearchJenkinsJob'}

    @logger.exception()
    def run(self, context) -> (str, list):
        service_params = Service().get_params(context.get_local('agent_id'), 'jenkins')
        url = service_params.get('fetch_job_name_url')
        timeout = service_params.get('timeout', 60)
        headers = service_params.get('headers')
        data = []
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            jobs = [job['name'] for job in response.json()['jobs']]
            query = context.get_local('jenkins_query_substring', 'dev')
            for job in jobs:
                if query.lower() in job.lower() and 'dev' in job:
                    data.append(job)
            code = 'success'
        except Exception as e:
            code = 'failure'

        return code, data


class RunJenkinsJob(Action):
    __mapper_args__ = {'polymorphic_identity': 'RunJenkinsJob'}

    @logger.exception()
    def run(self, context) -> (bool, any):
        service_params = Service().get_params(context.get_local('agent_id'), 'jenkins')
        jenkins_job_name = context.get_local('jenkins_job_name')

        if 'dev' not in jenkins_job_name:
            return False

        url = service_params.get('run_job_url').format(**locals())
        timeout = service_params.get('timeout', 60)
        headers = service_params.get('headers')

        code = 'failure'

        response = requests.post(url, headers=headers, timeout=timeout)

        if response.status_code == '201':
            code = 'success'

        return code, None
