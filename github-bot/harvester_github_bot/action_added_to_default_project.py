from harvester_github_bot.issue_transfer import IssueTransfer
from harvester_github_bot.action import Action
from harvester_github_bot import app, gtihub_project_manager, \
    ZENHUB_PIPELINE, ZENHUB_PIPELINE

class ActionAddedToDefaultProject(Action):
    def __init__(self):
        pass
    
    def isMatched(self, actionRequest):
        if actionRequest.event_type not in ['issue']:
            return False
        if actionRequest.action not in ['opened']:
            return False
        return True
    
    def action(self, request):
        if gtihub_project_manager.prepared is False:
            return

        issue = request.get('issue')
        item = gtihub_project_manager.get_issue(issue["number"])
        gtihub_project_manager.add_issue_to_project(item['id'])