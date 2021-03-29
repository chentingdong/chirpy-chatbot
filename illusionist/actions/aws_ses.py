from illusionist.models.action import Action
from python_utils.logger import logger, logger_console
from illusionist.models.service import Service
import boto3
from botocore.exceptions import ClientError


class AwsSesSendEmail(Action):
    __mapper_args__ = {'polymorphic_identity': 'AwsSesSendEmail'}
    service_name = 'aws_ses'

    @logger.exception()
    def run(self, context):
        return aws_ses_send(context, self.service_name), None


def aws_ses_send(context, service_name):
    email_content = prepare_email(context, service_name)
    service_params = Service().get_params(context.get_local('agent_id'), service_name)
    sender = service_params.get('sender_email')
    recipient = context.get_local('user_email')
    raw_format = service_params.get('formatted', True)
    charset = 'UTF-8'

    ses = boto3.client(
        "ses",
        aws_access_key_id=service_params.get('aws_access_key_id'),
        aws_secret_access_key=service_params.get('aws_secret_access_key'),
        region_name=service_params.get('region_name')
    )

    if raw_format:
        try:
            ses.send_email(
                Destination={
                    'ToAddresses': [
                        recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': charset,
                            'Data': email_content.get('body'),
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': email_content.get('subject'),
                    },
                },
                Source=sender,
            )
        except ClientError as e:
            logger_console.error(e)
            return 'failure'

        return 'success'


def prepare_email(context, service_name):
    service_params = Service().get_params(context.get_local('agent_id'), service_name)
    subject = service_params.get('subject')
    body = service_params.get('body').format(context.get_local('view_url'))
    email_content = {'subject': subject, 'body': body}
    return email_content

