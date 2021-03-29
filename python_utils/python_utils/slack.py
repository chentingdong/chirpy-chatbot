import slack
from python_utils.config import server_config
from python_utils.logger import logger_console


class Slack:

    def __init__(self):
        """ See all API method here: https://api.slack.com/methods """
        self.bot_token = server_config['slack']['token']

    def post_message(self, msg, receiver, as_user=False):
        sc = slack.WebClient(self.bot_token)
        post_msg = sc.chat_postMessage(channel=receiver, text=str(msg), as_user=as_user)
        logger_console.info("posted", post_msg.data)
        return post_msg


slack_messager = Slack()
