"""
Main module for Flambda APP
Version: 1.0.0
"""

import os
from dotenv import dotenv_values


def load_projectrc(projectrc_filepath):
    """
    Load the values of .projectrc file
    """
    return dotenv_values(projectrc_filepath)


if __package__:
    CURRENT_PATH = os.path.abspath(os.path.dirname(__file__)).replace('/' + str(__package__), '', 1)
else:
    CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

ENV_VARS = {}
PROJECTRC_FILE = os.path.join(CURRENT_PATH, '.projectrc')

# Inside a Docker container, the folder name is 'app'
PROJECT_NAME = os.path.basename(CURRENT_PATH).replace('_', '-')

if not CURRENT_PATH.endswith('/'):
    CURRENT_PATH += '/'

if os.path.exists(PROJECTRC_FILE):
    ENV_VARS = load_projectrc(PROJECTRC_FILE)

APP_NAME = ENV_VARS.get('APP_NAME', PROJECT_NAME)
APP_VERSION = ENV_VARS.get('APP_VERSION', '1.0.0')
APP_ARCH_VERSION = ENV_VARS.get('APP_ARCH_VERSION', 'v1')
