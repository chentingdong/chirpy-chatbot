from slackclient import SlackClient
from yaml_reader import getProperty


#def slack_notification(message: object) -> object:
def slack_notification(message):
    slack_token = getProperty('Slack_token')
    sc = SlackClient(slack_token)
    sc.api_call(
        "chat.postMessage",
        channel=getProperty('Slack_recipient'),
        text=message
    )

