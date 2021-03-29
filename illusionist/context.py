from python_utils.logger import logger_console


class Context:
    def __init__(self):
        self.stack = []
        self.state_history = []
        self.converstion_history = []
        self.bot_history = []
        self.answers = []
        self.local_variables = {}

    def clear(self):
        self.__init__()

    def reset(self):
        self.local_variables = {}
        self.answers = []

    def get_local(self, key: str, default: any=None) -> object:
        if key == 'context':
            return self
        value = self.local_variables.get(key, '')
        if not value:
            value = default
        return value

    def set_local(self, key: str, value: object):
        if key == 'context':
            logger_console.error('Can not set context in local')
            return
        self.local_variables[key] = value

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)
