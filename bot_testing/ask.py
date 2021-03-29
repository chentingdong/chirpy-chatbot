import requests
import json
import time
from python_utils.logger import logger_console
from python_utils.config import server_config
import os


# illusionist ask endpoint
def ask_api(sys_id, bot_id, utterance, bot_name):
    try:
        
        url = server_config['illusionist']['host']+'/api/1/ask_bot/{}'.format(bot_id)
        querystring = {"session_id": str(sys_id)}
        headers = {"Content-Type": "application/json"}
        payload = get_ask_payload(utterance, bot_name)
        req = requests.post(url, data=json.dumps(payload), headers=headers, params=querystring)
        if req.status_code != 200:
            raise Exception('Illusionist ask api failed with status code {}'.format(req.status_code))
        response = json.loads(req.text)
        time.sleep(3)
        return response['payloads']['answer']
    except Exception as e:
        logger_console.error("Illusionist ask api failed: {}".format(e))


# ask payload
def get_ask_payload(utterance, bot_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(dir_path+'/payload.json')
    payload = json.load(file)
    payload.update({"utterance": utterance})
    payload.update({"bot_name": bot_name})
    return payload
