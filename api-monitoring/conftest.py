from test_bot_Info import *


def pytest_addoption(parser):
    parser.addoption("--env", action="append",
                     help="Available environments: 'https://api-dev.aineva.com/illusionist/',"
                          "'https://api-stg.aineva.com/illusionist/'")

    parser.addoption("--conversation", action="append",
                     help="Available conversations: 2, 3, 5,9,all")

    parser.addoption("--workflow", action="append",
                     help="Available workflows : 'main_flow','adidas'")


def pytest_generate_tests(metafunc):

    if 'env' in metafunc.fixturenames:
        env = set(metafunc.config.option.env)
        for item in env:
            if item not in getEnvironmentsList():
                raise ValueError('invalid environment')
            else:
                env = list(env)
        metafunc.parametrize('env', env)

    if 'conversation' in metafunc.fixturenames:
        list1 = getConversationList()
        cid = set(metafunc.config.option.conversation)
        for item in cid:
            if 'all' in cid:
                cid = list1
            elif int(item) not in getConversationList():
                raise ValueError('invalid conversation id')
            else:
                cid = list(cid)
        metafunc.parametrize('conversation', cid)

    if 'workflow' in metafunc.fixturenames:
        workflow = set(metafunc.config.option.workflow)
        # for item in workflow:
        #     if item not in getWorkflowsList():
        #         raise ValueError('invalid workflow')
        #     else:
        workflow = list(workflow)
        metafunc.parametrize('workflow', list(workflow))
