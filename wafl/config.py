import os

_path = os.path.dirname(__file__)
_rules_template = open(os.path.join(_path, 'templates/rules.wafl'))
_server_template = open(os.path.join(_path, 'templates/server.py'))
_functions_template = open(os.path.join(_path, 'templates/functions.py'))


def create_initial_files():
    print('+ Initializing ... ', end='')

    with open('rules.wafl', 'w') as file:
        file.write(_rules_template.read())

    with open('server.py', 'w') as file:
        file.write(_server_template.read())

    with open('functions.py', 'w') as file:
        file.write(_functions_template.read())

    print('Done.')
