from harvester_github_bot import app
from harvester_github_bot import zenh_api, repo

sync_milestone_to_releases_actions = ['opened', 'milestoned', 'demilestoned']


def sync_milestone_to_releases(req):
    issue = req.get('issue')
    action = req.get('action')
    if action not in sync_milestone_to_releases_actions:
        return ""

    if issue['milestone'] is not None:
        app.logger.debug('set releases: repo.id=%d, milestone=%s, number=%s',
                         repo.id,
                         issue['milestone']['title'],
                         issue["number"])
        return zenh_api.clean_releases_to_issue_except_by_milestone(repo.id, issue['milestone']['title'],
                                                                    issue["number"])

    app.logger.debug('clean releases: repo.id=%d, number=%s', repo.id, issue["number"])
    return zenh_api.clean_releases_to_issue_except_by_milestone(repo.id, "", issue["number"])
