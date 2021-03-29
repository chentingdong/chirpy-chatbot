import yaml
import os


def getProperty(value):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/configuration.yml', 'r') as stream:
        try:
            data = yaml.load(stream)
            return data['TestData'][value]
        except yaml.YAMLError as exc:
            print(exc)
