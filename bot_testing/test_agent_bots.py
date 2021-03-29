from deepdiff import DeepDiff
from bot_testing.bot_methods import *
from python_utils.logger import logger_console
from python_utils.config import server_config
import unittest


class Test(unittest.TestCase):

    def test_agent_bot(self):
        """
           Test bots using Agent_id
        """
        try:
            agent_list = server_config['illusionist']['agents']
            logger_console.info('Agent List: {}'.format(agent_list))
            status = []
            bots = []
            for agent_id in agent_list:
                logger_console.info('Test Agent Id is: {}'.format(agent_id))
                recorded_test = get_recorded_data(agent_id)
                for data in recorded_test:
                    bot_id = data[0]
                    logger_console.info('Test Bot Id is: {}'.format(bot_id))
                    bot_name = data[1]
                    test_set = data[2]
                    logger_console.info('Test Bot name is: {}'.format(bot_name))
                    utterances = get_expected_utterances(test_set)
                    expected_response = get_expected_response(test_set)
                    actual_response = get_actual_response(utterances, bot_id, bot_name)
                    diff = DeepDiff(expected_response, actual_response)
                    update_test_status_db(diff, bot_id)
                    status.append(diff_status(diff))
                    if not diff_status(diff):
                        bots.append(bot_name)
            assert all(status)
        except AssertionError as e:
            raise AssertionError('Failed bots are {}'.format(bots))


if __name__ == '__main__':
    unittest.main()