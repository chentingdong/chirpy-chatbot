import enum


class ServiceEnum(enum.Enum):
    """
    Edit this class to add or delete service types
    """
    SERVICE_NOW = 'SERVICE_NOW'
    JIRA = 'JIRA'
    SLACK = 'SLACK'

    def __repr__(self):
        return str(self.__class__) + ': ' + self.name

    @classmethod
    def default(cls):
        return cls.SERVICE_NOW
