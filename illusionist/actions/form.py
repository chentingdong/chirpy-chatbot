from illusionist.models.action import Action
from python_utils.logger import logger, logger_console


class FormPreview(Action):
    __mapper_args__ = {'polymorphic_identity': 'FormPreview'}

    @logger.exception()
    def run(self, context) -> (str, dict):
        logger_console.info(context)
        return 'success', context.get_local('form')
