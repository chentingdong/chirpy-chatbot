from yaml_reader import getProperty
import requests
import simplejson as json
from slack_notification import slack_notification


def test_smoke(env, conversation, workflow):
    """ Smoketest script for illusionist conversation"""
    try:
        payload = {"host": env, "workflow": workflow}
        print(getProperty('Jenkins_Host').format(conversation))
        print(payload)
        r = requests.post(getProperty('Jenkins_Host').format(conversation),
                          json.dumps(payload),
                          headers=getProperty('Headers'))
        print("Response code is "+str(r.status_code))
        print('Response Time for request is ' + str(r.elapsed.total_seconds()))
        if r.status_code != 200:
            message = 'Illusionist Request Failed \n' + 'Host: ' + getProperty('Jenkins_Host').format(conversation) + '\n' \
                      + 'Status Code for request is: ' + str(r.status_code) + '\n' + 'Error is: ' \
                      + str(r.text) + '\n' + '#########################'
            slack_notification(message)
        elif r.status_code == 200:
            # assert r.status_code == 200
            response = json.loads(r.text)
            for item in range(0, len(response['data'])):
                if response['data'][item]['expectedResponse']['answers'] != response['data'][item]['response']['answers']:
                    message = 'Responses are not matching with expected responses \n' + 'Host: ' + getProperty('Jenkins_Host').format(
                        conversation)
                    slack_notification(message)
                    assert response['data'][item]['expectedResponse']['answers'] == response['data'][item]['response'][
                        'answers']
                    break
            print("####################")

    except ConnectionError as e:
        slack_notification("ConnectionError: {}".format(e))
    except requests.exceptions.Timeout as e:
        slack_notification("Timeout Error: {}".format(e))
    except requests.exceptions.RequestException as e:
        slack_notification("Error: {}".format(e))
