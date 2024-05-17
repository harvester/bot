from harvester_github_bot import app
from harvester_github_bot import zenh_api, repo
from harvester_github_bot.exception import CustomException

class ActionSyncMilestone:
    def __init__(self):
        pass
    def isMatched(self, actionRequest):
        if actionRequest.action not in ['opened', 'milestoned', 'demilestoned']:
            return False
        return True
    def action(self, request):
        return sync_milestone(request)
    
def sync_milestone(request):
    issue = request.get('issue')
    milestone = issue['milestone']
    milestone_title = milestone['title'] if milestone is not None else ""
    
    if milestone_title != "":
        app.logger.debug('set releases: repo.id=%d, milestone=%s, number=%s',
                         repo.id,
                         milestone_title,
                         issue["number"])
    else:
        app.logger.debug('clean releases: repo.id=%d, number=%s', repo.id, issue["number"])
    
    try: 
        zenh_api.clean_releases_to_issue_except_by_milestone(
            repo.id, milestone_title, issue["number"]
        )
        return "sync milestone success"
    except CustomException as e:
        app.logger.exception(f"Custom exception : {str(e)}")
    except Exception as e:
        app.logger.exception(e)

    return "sync milestone failed"