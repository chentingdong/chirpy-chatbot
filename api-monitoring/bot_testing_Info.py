import requests
import simplejson as json
from yaml_reader import getProperty
from slack_notification import slack_notification


def getConversationList():
    """Method for retrieving conversation id's list from bot testing framework UI"""
    try:
        conversation_id = []
        r = requests.get(getProperty('api_conversation'))
        if r.status_code != 200:
            message = 'Illusionist Request Failed \n' + 'Host: ' + getProperty('api_conversation') + '\n' \
                      + 'Status Code for request is: ' + str(r.status_code) + '\n' + 'Error is: ' \
                      + str(r.text) + '\n' + '#########################'
            slack_notification(message)
            return conversation_id
        elif r.status_code == 200:
            response = json.loads(r.text)
            size = len(response['data']['results'])
            conversation_id = []
            for item in range(0, size):
                conversation_id.append(response['data']['results'][item]['id'])
            return conversation_id
    except ConnectionError as e:
        slack_notification("ConnectionError: {}".format(e))
    except requests.exceptions.Timeout as e:
        slack_notification("Timeout Error: {}".format(e))
    except requests.exceptions.RequestException as e:
        slack_notification("Error: {}".format(e))


def getEnvironmentsList():
    """Method for retrieving Environments List from bot testing framework UI"""
    try:
        environments_list = []
        r = requests.get(getProperty('api_environment'))
        if r.status_code != 200:
            message = 'Illusionist Request Failed \n' + 'Host: ' + getProperty('api_environment') + '\n' \
                      + 'Status Code for request is: ' + str(r.status_code) + '\n' + 'Error is: ' \
                      + str(r.text) + '\n' + '#########################'
            # slack_notification(message)
            return environments_list
        elif r.status_code == 200:
            response = json.loads(r.text)
            size = len(response['data']['results'])
            environments_list = []
            for item in range(0, size):
                environments_list.append(response['data']['results'][item]['host'])
            return environments_list
    except ConnectionError as e:
        slack_notification("ConnectionError: {}".format(e))
    except requests.exceptions.Timeout as e:
        slack_notification("Timeout Error: {}".format(e))
    except requests.exceptions.RequestException as e:
        slack_notification("Error: {}".format(e))


# def getWorkflowsList():
#     """Method for retrieving workflows List from bot testing framework UI"""
#     try:
#         workflows_list = []
#         r = requests.get(getProperty('api_workflow'))
#         if r.status_code != 200:
#             message = 'Illusionist Request Failed \n' + 'Host: ' + getProperty('api_workflow') + '\n' \
#                       + 'Status Code for request is: ' + str(r.status_code) + '\n' + 'Error is: ' \
#                       + str(r.text) + '\n' + '#########################'
#             slack_notification(message)
#             return workflows_list
#         elif r.status_code == 200:
#             response = json.loads(r.text)
#             size = len(response['payloads']['result'])
#             for item in range(0, size):
#                 workflows_list.append(response['payloads']['result'][item]['name'])
#             return workflows_list
#     except ConnectionError as e:
#         slack_notification("ConnectionError: {}".format(e))
#     except requests.exceptions.Timeout as e:
#         slack_notification("Timeout Error: {}".format(e))
#     except requests.exceptions.RequestException as e:
#         slack_notification("Error: {}".format(e))
