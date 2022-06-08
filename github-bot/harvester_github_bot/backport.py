import re

from harvester_github_bot import zenh_api, repo, \
    BACKPORT_LABEL_KEY

# check the issue's include backport-needed/(1.0.3|v1.0.3|v1.0.3-rc0) label
backport_label_pattern = r'^%s\/[\w0-9\.]+' % BACKPORT_LABEL_KEY


# link: https://github.com/harvester/harvester/issues/2324
# Title: [Backport v1.x] copy-the-title.
# Description: backport the issue #link-id
# Copy assignees and all labels except the backport-needed and add the not-require/test-plan label.
# Move the issue to the associated milestone and release.
def backport(obj):
    bp = Backport(obj['issue']['number'], obj['issue']['labels'])

    err = bp.verify()
    if err != "":
        return err

    err = bp.create_issue_if_not_exist()
    if err != "":
        return err

    bp.create_comment()
    return bp.related_release()


class Backport:
    def __init__(
            self,
            issue_number,
            labels
    ):
        self.__issue = None
        self.__origin_issue = repo.get_issue(issue_number)
        self.__labels = [repo.get_label("not-require/test-plan")] + \
                        [repo.get_label(label["name"]) for label in labels]

        self.__backport_needed, self.__ver = {}, ""
        self.__parse_ver()

        self.__milestone = {}
        self.__parse_milestone()

    def __parse_ver(self):
        for idx, label in enumerate(self.__labels):
            if re.match(backport_label_pattern, label.name) is not None:
                self.__backport_needed = self.__labels.pop(idx)
                self.__ver = self.__backport_needed.name.split("/")[1]
                break

        if self.__ver == "":
            return
        if not self.__ver.startswith("v"):
            self.__ver = "v" + self.__ver

    def __parse_milestone(self):
        if self.__ver == "":
            return

        milestones = repo.get_milestones(state='open')
        for ms in milestones:
            if ms.title == self.__ver:
                self.__milestone = ms
                break

    def verify(self):
        if self.__ver == "":
            return "not found any version"
        if self.__ver == self.__origin_issue.milestone.title:
            return "backport version already exists in the currently issue."

        return ""

    def create_issue_if_not_exist(self):
        title = "[backport %s] %s" % (self.__ver, self.__origin_issue.title)
        body = "backport the issue #%s" % self.__origin_issue.number

        # return if the comment exists
        comment_pattern = r'added `%s` issue: #[\d].' % self.__backport_needed.name
        comments = self.__origin_issue.get_comments()
        for comment in comments:
            if re.match(comment_pattern, comment.body):
                return "exists backport comment with %s" % self.__ver

        self.__issue = repo.create_issue(title=title,
                                         body=body,
                                         milestone=self.__milestone,
                                         labels=self.__labels,
                                         assignees=self.__origin_issue.assignees
                                         )
        return ""

    def create_comment(self):
        self.__origin_issue.create_comment(
            body='added `%s` issue: #%d.' % (self.__backport_needed.name, self.__issue.number))

    # associated zenhub releases
    def related_release(self):
        release_id, err = zenh_api.get_release_id_by_version(repo_id=repo.id, version=self.__ver)
        if err != "":
            return err

        if release_id is not None and len(release_id) > 0:
            res = zenh_api.add_release_to_issue(repo_id=repo.id, release_id=release_id,
                                                issue_number=self.__issue.number)
            if res != "":
                return "failed to associated release(%s) with repo(%d) and issue(%d): %s" % (
                    release_id, repo.id, self.__issue.number, res)

        return "issue number: %d." % self.__issue.number
