import logging

from flask import Flask
from everett.component import RequiredConfigMixin, ConfigOptions
from everett.manager import ConfigManager, ConfigOSEnv
from werkzeug.security import generate_password_hash
from github import Github
from harvester_github_bot.github_graphql.manager import GitHubProjectManager
from harvester_github_bot.zenhub import Zenhub

FLASK_LOGLEVEL = ""
FLASK_PASSWORD = ""
FLASK_USERNAME = ""
GITHUB_OWNER = ""
GITHUB_REPOSITORY = ""
GITHUB_REPOSITORY_TEST = ""
GITHUB_PROJECT_NUMBER = ""
ZENHUB_PIPELINE = ""
BACKPORT_LABEL_KEY = ""

app = Flask(__name__)
gh_api = {}
zenh_api = {}
repo = {}
repo_test = {}
gtihub_project_manager = {}

class BotConfig(RequiredConfigMixin):
    required_config = ConfigOptions()
    required_config.add_option('flask_loglevel', parser=str, default='info', doc='Set the log level for Flask.')
    required_config.add_option('flask_password', parser=str, doc='Password for HTTP authentication in Flask.')
    required_config.add_option('flask_username', parser=str, doc='Username for HTTP authentication in Flask.')
    required_config.add_option('github_owner', parser=str, default='harvester',
                               doc='Set the owner of the target GitHub '
                                   'repository.')
    required_config.add_option('github_repository', parser=str, default='harvester', doc='Set the name of the target '
                                                                                         'GitHub repository.')
    required_config.add_option('github_repository_test', parser=str, default='tests', doc='Set the name of the tests '
                                                                                          'GitHub repository.')
    required_config.add_option('github_project_number', parser=int, doc='Set the project id of the github '
                                                                                          'GitHub Project ID.')
    required_config.add_option('github_token', parser=str, doc='Set the token of the GitHub machine user.')
    required_config.add_option('zenhub_pipeline', parser=str, default='Review,Ready For Testing,Testing',
                               doc='Set the target ZenHub pipeline to '
                                   'handle events for.')
    required_config.add_option('zenhub_token', parser=str, doc='Set the token of the ZenHub machine user.')
    required_config.add_option('backport_label_key', parser=str, default='backport-needed',
                               doc='Set the backport label key.')


def get_config():
    c = ConfigManager(environments=[
        ConfigOSEnv()
    ])
    return c.with_options(BotConfig())


def settings():
    global FLASK_LOGLEVEL, FLASK_PASSWORD, FLASK_USERNAME, GITHUB_OWNER, GITHUB_REPOSITORY, GITHUB_PROJECT_NUMBER, GITHUB_REPOSITORY_TEST, \
        ZENHUB_PIPELINE, BACKPORT_LABEL_KEY, gh_api, zenh_api, repo, repo_test, gtihub_project_manager
    config = get_config()
    FLASK_LOGLEVEL = config('flask_loglevel')
    FLASK_PASSWORD = generate_password_hash(config('flask_password'))
    FLASK_USERNAME = generate_password_hash(config('flask_username'))
    GITHUB_OWNER = config('github_owner')
    GITHUB_REPOSITORY = config('github_repository')
    GITHUB_REPOSITORY_TEST = config('github_repository_test')
    GITHUB_PROJECT_NUMBER = config('github_project_number')
    ZENHUB_PIPELINE = config('zenhub_pipeline')
    BACKPORT_LABEL_KEY = config('backport_label_key', default='backport-needed')

    gh_api = Github(config('github_token'))
    zenh_api = Zenhub(config('zenhub_token'))
    repo = gh_api.get_repo('{}/{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY))
    repo_test = gh_api.get_repo('{}/{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY_TEST))
    gtihub_project_manager = GitHubProjectManager(GITHUB_OWNER, GITHUB_REPOSITORY, GITHUB_PROJECT_NUMBER, {
        'Authorization': f'Bearer {config("github_token")}',
        'Content-Type': 'application/json'
    })

    numeric_level = getattr(logging, FLASK_LOGLEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('invalid log level: %s'.format(FLASK_LOGLEVEL))
    app.logger.setLevel(level=numeric_level)

settings()
