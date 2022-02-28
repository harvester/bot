from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from github import Github
from werkzeug.security import generate_password_hash, check_password_hash

from harvester_github_bot.config import get_config

import logging
import re

app = Flask(__name__)
auth = HTTPBasicAuth()

config = get_config()
FLASK_LOGLEVEL = config('flask_loglevel')
FLASK_PASSWORD = generate_password_hash(config('flask_password'))
FLASK_USERNAME = generate_password_hash(config('flask_username'))
GITHUB_OWNER = config('github_owner')
GITHUB_REPOSITORY = config('github_repository')
GITHUB_REPOSITORY_TEST = config('github_repository_test')
ZENHUB_PIPELINE = config('zenhub_pipeline')

# From https://docs.python.org/3/howto/logging.html#logging-to-a-file
numeric_level = getattr(logging, FLASK_LOGLEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('invalid log level: %s'.format(FLASK_LOGLEVEL))
app.logger.setLevel(level=numeric_level)

g = Github(config('github_token'))

template_re = re.compile('---\n.*?---\n', re.DOTALL)

@auth.verify_password
def verify_password(username, password):
    if check_password_hash(FLASK_USERNAME, username) and check_password_hash(FLASK_PASSWORD, password):
        return username


@app.route('/zenhub', methods=['POST'])
@auth.login_required
def zenhub():
    form = request.form
    organization = form.get('organization')
    repo = form.get('repo')
    if organization != GITHUB_OWNER or repo != GITHUB_REPOSITORY:
        app.logger.debug("webhook event targets %s/%s, ignoring", organization, repo)
    else:
        webhook_type = request.form.get('type')
        if webhook_type == 'issue_transfer':
            issue_transfer(form)
        else:
            app.logger.debug('unhandled webhook type %s, ignoring', webhook_type)

    return {
        'message': 'webhook handled successfully'
    }, 200


def issue_transfer(form):
    issue_number = form.get('issue_number')
    try:
        issue_number = int(issue_number)
    except ValueError:
        app.logger.warning('could not parse issue_number %s as int', issue_number)
        return
    pipeline = form.get('to_pipeline_name')
    if pipeline not in ZENHUB_PIPELINE.split(","):
        app.logger.debug('to_pipeline is {}, ignoring'.format(pipeline))
        return

    repo = g.get_repo('{}/{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY))
    issue = repo.get_issue(issue_number)
    comments = issue.get_comments()
    found = False
    for comment in comments:
        if comment.body.strip().startswith('## Pre Ready-For-Testing Checklist'):
            app.logger.debug('pre-merged checklist already exists, not creating a new one')
            found = True
            break
    if not found:
        app.logger.debug('pre-merge checklist does not exist, creating a new one')
        issue.create_comment(render_template('pre-merge.md'))

    require_e2e = True
    labels = issue.get_labels()
    for label in labels:
        if label.name == 'not-require/test-plan':
            require_e2e = False
            break
    if require_e2e:
        found = False
        for comment in comments:
            if comment.body.startswith('Automation e2e test issue:'):
                app.logger.debug('Automation e2e test issue already exists, not creating a new one')
                found = True
                break
        if not found:
            app.logger.debug('Automation e2e test issue does not exist, creating a new one')
            issue_link = '{}/{}#{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY, issue_number)
            issue_test_title = '[e2e] {}'.format(issue.title)
            repo_test = g.get_repo('{}/{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY_TEST))
            issue_test_template_content = repo_test.get_contents(".github/ISSUE_TEMPLATE/test.md").decoded_content.decode()
            issue_test_body = template_re.sub("\n", issue_test_template_content, count=1)
            issue_test_body += '\nrelated issue: {}'.format(issue_link)
            issue_test = repo_test.create_issue(title=issue_test_title, body=issue_test_body)
            issue_test_link = '{}/{}#{}'.format(GITHUB_OWNER, GITHUB_REPOSITORY_TEST, issue_test.number)
            # link test issue in Harvester issue
            issue.create_comment('Automation e2e test issue: {}'.format(issue_test_link))
    else:
        app.logger.debug('label require/automation-e2e does not exists, not creating test issue')
