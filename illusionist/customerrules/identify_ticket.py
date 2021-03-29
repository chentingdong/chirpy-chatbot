import re
from illusionist.customerrules.customer_rule import CustomerRule
from illusionist.models.action import Action
from illusionist.bot_engine import BotEngine
from illusionist.actions.servicenow import ServiceNowIncidentGetStatusById
from python_utils.logger import logger_console
from illusionist.models.service import Service


class IdentifyTicket(CustomerRule):

    def apply(self, context, services):
        """
        Sample agent_config for a customer_rule
        {
            "customer_rules": {
                "IdentifyTicket": [
                    "servicenow"
                ]
             }
        }
        """
        for service_name in services:
            code = ServiceOfRecord(IdentifyTicket.get_service_class(service_name)).identify_ticket(context, service_name)
            if code == "ticket_found":
                bot_engine = BotEngine()
                utterance_length = len(context.get_local('utterance').split())
                # ToDo: Bot names harcoded for now and should be same for all agents using this feature
                if utterance_length > 1:
                    logger_console.info("Assigning to bot {}".format('confirm.check.ticket.status'))
                    bot_engine.assign_bot(context, 'ticket.status:confirm')
                else:
                    logger_console.info("Assigning to bot {}".format('check.ticket.status'))
                    bot_engine.assign_bot(context, 'ticket.status:check')
                return True
            elif code == "ticket_not_found":
                bot_engine = BotEngine()
                bot_engine.assign_bot(context, 'ticket.status:not.found')
                return True

    @staticmethod
    def get_service_class(service_name):
        service_class_mapper = {"servicenow": ServiceNow}
        return service_class_mapper.get(service_name)


class ServiceOfRecord:
    """A strategy class. All the future implementation classes like cherwell,
    jira can implement this class and override identity_ticket method"""

    def __init__(self, strategy) -> None:
        self._strategy = strategy()

    def identify_ticket(self, context, service_name) -> str:
        return self._strategy.identify_ticket(context, service_name)


class ServiceNow(ServiceOfRecord):

    # class level default
    ticket_status = {
        "regex": "(inc|hrc|fr)\\d+",
        "domain_mapping": {
            "inc": "IT",
            "hrc": "HR",
            "fr": "FINANCE"
        }
    }

    regex = "(inc|hrc|fr)\\d+"

    def __init__(self):
        pass

    def identify_ticket(self, context, service_name) -> str:
        utterance = context.get_local('utterance')
        service_params = Service().get_params(context.get_local('agent_id'), service_name)
        regex = re.compile(service_params.get('ticket_status', {}).get('regex', self.ticket_status.get('regex')), re.I)
        match = re.search(regex, utterance)
        if match:
            ticket_number = match.group()
            context.set_local('servicenow_incident_id', ticket_number)
            luke_answer = {'data': {'domain': self.extract_domain(service_params, match)}}
            context.set_local('luke_answer', luke_answer)
            logger_console.info('Extracted {} as ticket number of {} from {} with regex {}'
                                .format(ticket_number, context.get_local('domain'), utterance, regex))
            code, results = ServiceNowIncidentGetStatusById.run(
                Action.query.filter_by(name=ServiceNowIncidentGetStatusById.__name__).first(), context)
            if code == 'success':
                logger_console.info('{} is a valid ticket'.format(ticket_number))
                return "ticket_found"
            else:
                logger_console.info('{} is not found in the service of record'.format(ticket_number))
                return "ticket_not_found"
        else:
            logger_console.info('No ticket match found in {} with regex {}'.format(utterance, regex))
            return "no_match"

    def extract_domain(self, service_params, match):
        domain_mapping = service_params.get('ticket_status', {}).get('domain_mapping', self.ticket_status.get('domain_mapping'))
        return domain_mapping.get(match.group(1).lower(), 'IT')
