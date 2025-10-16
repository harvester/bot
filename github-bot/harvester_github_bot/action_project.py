from harvester_github_bot.issue_transfer import IssueTransfer
from harvester_github_bot.action import Action
from harvester_github_bot import app, development_project_manager, \
    community_project_manager, repo, E2E_PIPELINE

class ActionProject(Action):
    def __init__(self):
        self.__event_type_key = "projects_v2_item"
    
    def isMatched(self, actionRequest):
        if actionRequest.event_type not in [self.__event_type_key]:
            return False
        if actionRequest.action not in ['edited']:
            return False
        return True

    # In github projectv2, every status filed changed will trigger a projectv2 event
    # For example, changing a `Estimate` and `Status`.
    # But, we only care about the `Status` field.
    def action(self, request):
        if request[self.__event_type_key]["content_type"] != "Issue":
            return

        project_node_id = request[self.__event_type_key]['project_node_id']

        if development_project_manager.project()["id"] == project_node_id:
            self.action_harvester_project(request)
            return

        if community_project_manager.project()["id"] == project_node_id:
            self.action_community_project(request)
            return

    def action_harvester_project(self, request):
        if request['changes']['field_value']['field_name'] != "Status":
            return

        target_column = request['changes']['field_value']['to']
        if target_column["name"] not in E2E_PIPELINE.split(","):
            app.logger.debug('target_column is {}, ignoring'.format(target_column["name"]))
            return

        issue_node_id = request[self.__event_type_key]['content_node_id']
        issue = development_project_manager.get_global_issue(issue_node_id)

        if issue["number"] is None:
            app.logger.error("issue number is None")
            return

        it = IssueTransfer(issue["number"])
        it.create_comment_if_not_exist()

    def action_community_project(self, request):
        if request['changes']['field_value']['field_name'] != "Status":
            return

        target_column = request['changes']['field_value']['to']
        if target_column["name"] != "Resolved":
            app.logger.debug('target_column is {}, ignoring'.format(target_column["name"]))
            return

        issue_node_id = request[self.__event_type_key]['content_node_id']
        issue = community_project_manager.get_global_issue(issue_node_id)

        if issue["number"] is None:
            app.logger.error("issue number is None")
            return

        # Get the issue object from PyGithub
        gh_issue = repo.get_issue(issue["number"])

        # Skip if the issue already has a milestone
        if gh_issue.milestone is not None:
            app.logger.info('Issue #{} already has milestone: {}, skipping'.format(
                issue["number"], gh_issue.milestone.title))
            return

        # Get the "Planning" milestone
        milestones = repo.get_milestones(state='open')
        planning_milestone = None
        for ms in milestones:
            if ms.title == "Planning":
                planning_milestone = ms
                break

        if planning_milestone is None:
            app.logger.error("Target milestone not found")
            return

        # Add the "Planning" milestone to the issue
        gh_issue.edit(milestone=planning_milestone)
        app.logger.info('Added Planning milestone to issue #{}'.format(issue["number"]))
