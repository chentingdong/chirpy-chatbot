from python_utils.slack import Slack


def test_slack():
    msg = "hello from `slackclient==2.1.0`"
    receiver = "#python_slack_test"
    sc = Slack()
    res = sc.post_message(msg=msg, receiver=receiver, as_user=False)
    assert res['ok'] is True


if __name__ == '__main__':
    test_slack()