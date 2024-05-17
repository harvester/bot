from harvester_github_bot import app
from harvester_github_bot import zenh_api, repo
from harvester_github_bot.exception import CustomException
import re

CREATE_GUI_ISSUE_LABEL = "require-ui"

class CreateGUIIssue:
    def __init__(self):
        pass
    
    def isMatched(self, request):
        for label in request['issue']['labels']:
            if CREATE_GUI_ISSUE_LABEL  in label['name']:
                return True
        return False
            
    def action(self, request):
        self.labels = ["area/ui"]
        
        for label in request['issue']['labels']:
            if CREATE_GUI_ISSUE_LABEL not in label['name']:
                self.labels.append(label['name'])
    
        self.issue_number = request['issue']['number']
        self.original_issue = repo.get_issue(self.issue_number)
        
        if self.__is_gui_issue_exist():
            return "GUI issue already exist"
        self.__create_gui_issue()
        self.__create_comment()
        return "create GUI issue success"
    
    def __create_gui_issue(self):
        issue_data = {
            'title': f"[GUI] {self.original_issue.title}",
            'body': f"GUI Issue from #{self.issue_number}",
            'labels': self.labels,
            'assignees': self.original_issue.assignees,
        }
        if self.original_issue.milestone is not None:
            issue_data['milestone'] = self.original_issue.milestone
        self.gui_issue = repo.create_issue(**issue_data)
        
    def __create_comment(self):
        self.original_issue.create_comment(body=f"GUI issue created #{self.gui_issue.number}.")
        
    def __is_gui_issue_exist(self):
        comment_pattern = r'GUI issue created #[\d].'
        comments = self.original_issue.get_comments()
        for comment in comments:
            if re.match(comment_pattern, comment.body):
                return True
        return False