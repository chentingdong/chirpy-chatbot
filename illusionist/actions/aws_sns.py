import boto3
import string, random

from illusionist.models.action import Action
from illusionist.models.service import Service
from python_utils.logger import logger


class AwsSns2FA(Action):
    __mapper_args__ = {'polymorphic_identity': 'AwsSns2FA'}
    service_name = 'aws_sns'

    @logger.exception()
    def run(self, context) -> (str, None):
        code_2fa, context = aws_sns_send('2fa', context, self.service_name)
        return "success", code_2fa


class AwsSnsPassword(Action):
    __mapper_args__ = {'polymorphic_identity': 'AwsSnsPassword'}
    service_name = 'aws_sns'

    @logger.exception()
    def run(self, context) -> (str, None):
        password, context = aws_sns_send('password', context, self.service_name)
        return "success", password


class Confirm2FACode(Action):
    __mapper_args__ = {'polymorphic_identity': 'Confirm2FACode'}

    @logger.exception()
    def run(self, context) -> (str, None):
        if context.get_local('code_2fa') == context.get_local('code_2fa_confirm'):
            match = "success"
        else:
            match = "failure"

        return match, None


def aws_sns_send(msg_type, context, service_name):
    service_params = Service().get_params(context.get_local('agent_id'), service_name)
    phone_number = service_params.get('phone_number')
    context.set_local('phone_number', phone_number)

    sns = boto3.client(
        "sns",
        aws_access_key_id=service_params.get('aws_access_key_id'),
        aws_secret_access_key=service_params.get('aws_secret_access_key'),
        region_name=service_params.get('region_name')
    )

    if msg_type == '2fa':
        digits = service_params.get('digits_2fa')
        code_2fa = str(two_factor_code(digits))
        context.set_local('code_2fa', code_2fa)
        sns.publish(
            PhoneNumber=phone_number,
            Message="Here is your two factor code: {}.".format(code_2fa)
        )
        return code_2fa, context

    if msg_type == 'password':
        digits = service_params.get('digits_password')
        password = generate_password(digits)
        context.set_local('password', password)
        sns.publish(
            PhoneNumber=phone_number,
            Message="Here is your new password: {}.".format(password)
        )
        return password, context


def two_factor_code(digits):
    start = 10**(digits-1)
    end = 10**digits - 1
    code = random.randint(start, end)
    return code


def generate_password(digits):
    password = ''.join(random.choice(string.ascii_letters) for x in range(digits))
    return password
