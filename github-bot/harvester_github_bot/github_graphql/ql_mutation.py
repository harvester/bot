ADD_ISSUE_TO_PROJECT_MUTATION = """
mutation($project_id: ID!, $content_id: ID!) {
  addProjectV2ItemById(input: {projectId: $project_id, contentId: $content_id}) {
    item {
      id
    }
  }
}
"""