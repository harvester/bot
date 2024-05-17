from harvester_github_bot.label_action.create_gui_issue import CreateGUIIssue
from harvester_github_bot.label_action.create_backport import CreateBackport


ALL_LABEL_ACTIONS = [
    CreateBackport,
    CreateGUIIssue
]

class ActionLabel:
    def __init__(self):
        pass
    
    def isMatched(self, actionRequest):
        if actionRequest.action not in ['labeled']:
            return False
        return True
    
    def action(self, request):
        for label_action in ALL_LABEL_ACTIONS:
            __label_action = label_action()
            if __label_action.isMatched(request):
                __label_action.action(request)
            
        return "labeled related actions succeed"

