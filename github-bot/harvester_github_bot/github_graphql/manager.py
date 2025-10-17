import requests
from datetime import datetime, timezone, timedelta
from harvester_github_bot import app
from harvester_github_bot.github_graphql.ql_queries import GET_ISSUE_QUERY, GET_GLOBAL_ISSUE_QUERY, GET_ORGANIZATION_PROJECT_QUERY
from harvester_github_bot.github_graphql.ql_mutation import ADD_ISSUE_TO_PROJECT_MUTATION, MOVE_ISSUE_TO_STATUS, MOVE_ISSUE_TO_ITERATION

class GitHubProjectManager:
    def __init__(self, organization, repository, project_number, headers):
        self.organization = organization
        self.repository = repository
        self.headers = headers
        self.url = "https://api.github.com/graphql"
        self.__project = self.__get_orgnization_project(project_number)
        self.status_node_id, self.status = self.get_status_fields()
        self.sprint_node_id, self.sprint, self.sprint_iterations = self.get_sprint_fields()
            
    def get_status_fields(self):
            nodes = self.__project.get("fields").get("nodes")
            for node in nodes:
                if node.get("name") == "Status":
                    return node.get("id"), {option.get("name"): option.get("id") for option in node.get("options")}

    def get_sprint_fields(self):
            nodes = self.__project.get("fields").get("nodes")
            for node in nodes:
                # Sprint field might be named "Sprint".
                if node.get("name") in ["Sprint"]:
                    # For Iteration fields, the structure is different
                    # It has 'configuration' -> 'iterations'
                    configuration = node.get("configuration")
                    if configuration:
                        iterations = configuration.get("iterations", [])
                        sprint_dict = {
                            iteration.get("title"): iteration.get("id")
                            for iteration in iterations
                        }
                        # Return node_id, sprint dict, and full iterations list
                        return node.get("id"), sprint_dict, iterations
            return None, {}, []

    def project(self):
        return self.__project

    def get_issue(self, issue_number):
        variables = {
            'repo_owner': self.organization,
            'repo_name': self.repository,
            'issue_number': issue_number
        }
        response = requests.post(self.url, headers=self.headers, json={'query': GET_ISSUE_QUERY, 'variables': variables})
        if response.status_code == 200:
            return response.json()['data']['repository']['issue']
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.json()}")
        
    def get_global_issue(self, issue_node_id):
        variables = {
            'issue_node_id': issue_node_id
        }
        response = requests.post(self.url, headers=self.headers, json={'query': GET_GLOBAL_ISSUE_QUERY, 'variables': variables})
        if response.status_code == 200:
            return response.json()['data']['node']
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.json})")

    def add_issue_to_project(self, issue_id):
        variables = {
            'project_id': self.__project["id"],
            'content_id': issue_id
        }
        response = requests.post(self.url, headers=self.headers, json={'query': ADD_ISSUE_TO_PROJECT_MUTATION, 'variables': variables})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Mutation failed to run by returning code of {response.status_code}. {response.json()}")
        
    def move_issue_to_status(self, issue_id, status_name):
        variables = {
            'project_id': self.__project["id"],
            'item_id': issue_id,
            'field_id': self.status_node_id,
            'single_select_option_id': self.status[status_name]
        }
        
        response = requests.post(self.url, headers=self.headers, json={'query': MOVE_ISSUE_TO_STATUS, 'variables': variables})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Mutation failed to run by returning code of {response.status_code}. {response.json()}")

    def get_current_sprint(self):
        """Get the current sprint/iteration based on date and duration"""
        if not self.sprint or not self.sprint_iterations:
            app.logger.info("No sprint information available")
            return None
        
        now = datetime.now(timezone.utc)
        
        for iteration in self.sprint_iterations:
            start_date_str = iteration.get("startDate")
            duration = iteration.get("duration")
            
            if not start_date_str or not duration:
                continue
            
            try:
                # Parse the start date (format: YYYY-MM-DD)
                # GitHub returns date without time, so we need to make it timezone-aware
                start_date = datetime.fromisoformat(start_date_str)
                # Add UTC timezone to make it comparable with 'now'
                start_date = start_date.replace(tzinfo=timezone.utc)
                
                # Calculate end date: startDate + duration (in days)
                end_date = start_date + timedelta(days=duration)
                
                # Check if now is within the sprint period
                if start_date <= now < end_date:
                    return iteration.get("title")
                    
            except (ValueError, AttributeError, TypeError) as e:
                app.logger.warning(f"Failed to parse iteration data: {e}")
                continue
        
        app.logger.info("No current sprint found")
        return None

    def move_issue_to_sprint(self, issue_id, sprint_name):
        """Move an issue to a specific sprint"""
        if not self.sprint_node_id or sprint_name not in self.sprint:
            app.logger.warning(f"Sprint field not found or sprint '{sprint_name}' does not exist")
            return None
            
        variables = {
            'project_id': self.__project["id"],
            'item_id': issue_id,
            'field_id': self.sprint_node_id,
            'iteration_id': self.sprint[sprint_name]
        }
        
        response = requests.post(self.url, headers=self.headers, json={'query': MOVE_ISSUE_TO_ITERATION, 'variables': variables})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Mutation failed to run by returning code of {response.status_code}. {response.json()}")
    
    def __get_orgnization_project(self, project_number):
        variables = {
            'organization': self.organization,
            'project_number': project_number
        }
        response = requests.post(self.url, headers=self.headers, json={'query': GET_ORGANIZATION_PROJECT_QUERY, 'variables': variables})
        if response.status_code == 200:
            return response.json()['data']['organization']['projectV2']
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.json()}")
