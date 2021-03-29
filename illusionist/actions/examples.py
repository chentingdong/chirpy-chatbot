from datetime import datetime, timedelta
from illusionist.models.action import Action
from python_utils.logger import logger


class OrderPizza(Action):
    __mapper_args__ = {'polymorphic_identity': 'OrderPizza'}

    @logger.exception()
    def run(self, context) -> (str, dict):
        receipt = {
            'first_name': context.get_local('first_name'),
            'summary': context.get_local('short_description'),
            'deliver_time': str(datetime.now() + timedelta(minutes=11)),
            'deliver_address': context.get_local('deliver_address')
        }

        return 'success', receipt


class McDFormPreview(Action):
    pass