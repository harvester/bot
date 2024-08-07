import requests
from harvester_github_bot.github_graphql.ql_queries import GET_ISSUE_QUERY, GET_ORGANIZATION_PROJECT_QUERY, GET_USER_PROJECT_QUERY
from harvester_github_bot.github_graphql.ql_mutation import ADD_ISSUE_TO_PROJECT_MUTATION

class GitHubProjectManager:
    def __init__(self, organization, repository, project_number, headers):
        self.organization = organization
        self.repository = repository
        self.headers = headers
        self.url = "https://api.github.com/graphql"
        
        try:
            self.__project = self.__get_orgnization_project(project_number)
            self.prepared = True
        except:
            self.prepared = False

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


    def __get_user_project(self, project_number):
        variables = {
            'organization': self.organization,
            'project_number': project_number
        }
        response = requests.post(self.url, headers=self.headers, json={'query': GET_USER_PROJECT_QUERY, 'variables': variables})
        if response.status_code == 200:
            return response.json()['data']['user']['projectV2']
        else:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.json()}")