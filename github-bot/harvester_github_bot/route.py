import http

from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from harvester_github_bot.config import app, FLASK_USERNAME, FLASK_PASSWORD, GITHUB_OWNER, GITHUB_REPOSITORY
from harvester_github_bot.issue_transfer import issue_transfer
from harvester_github_bot.action import ActionRequest
from harvester_github_bot.action_label import ActionLabel
from harvester_github_bot.action_sync_milestone import ActionSyncMilestone
from harvester_github_bot.action_project import ActionProject

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if check_password_hash(FLASK_USERNAME, username) and check_password_hash(FLASK_PASSWORD, password):
        return username

@app.route('/zenhub', methods=['POST'])
@auth.login_required
def zenhub():
    form = request.form
    organization = form.get('organization')
    repo_name = form.get('repo')
    if organization != GITHUB_OWNER or repo_name != GITHUB_REPOSITORY:
        app.logger.debug("webhook event targets %s/%s, ignoring", organization, repo_name)
    else:
        webhook_type = request.form.get('type')
        if webhook_type == 'issue_transfer':
            issue_transfer(form)
        else:
            app.logger.debug('unhandled webhook type %s, ignoring', webhook_type)

    return {
               'message': 'webhook handled successfully'
           }, http.HTTPStatus.OK
SUPPORTED_ACTIONS = [
    ActionLabel(),
    ActionSyncMilestone(),
    ActionProject(),
]

SUPPORTED_EVENT = [
    "projects_v2_item",
    "issue"
]

@app.route('/github', methods=['POST'])
@auth.login_required
def gh():
    req = request.get_json()
    msg = "Skip action"
    event_type = ""
        
    for event in SUPPORTED_EVENT:
        if req.get(event) is not None:
            event_type = event
    
    if event_type == "":
        return {
            'message': msg
        }, http.HTTPStatus.OK
        
    action_request = ActionRequest(req.get('action'), event_type)
    
    for action in SUPPORTED_ACTIONS:
        if action.isMatched(action_request):
            msg = action.action(req)
            break

    if msg != "":
        app.logger.debug(msg)
        return {
            'message': msg
        }, http.HTTPStatus.OK

    return {}, http.HTTPStatus.OK
