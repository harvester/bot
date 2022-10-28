import requests
import http
import json

ZENHUB_DEFAULT_BASE_URL = "https://api.zenhub.com"
ZENHUB_DEFAULT_TIMEOUT = 15

ZENHUB_PATH_GET_ISSUE_DATA = ZENHUB_DEFAULT_BASE_URL + "/p1/repositories/%d/issues/%d"

ZENHUB_PATH_GET_RELEASES = ZENHUB_DEFAULT_BASE_URL + "/p1/repositories/%d/reports/releases"
ZENHUB_PATH_ADD_OR_REMOVE_ISSUE_FROM_RELEASE = ZENHUB_DEFAULT_BASE_URL + "/p1/reports/release/%s/issues"


def error(status_code, wrap=""):
    if status_code == http.HTTPStatus.NOT_FOUND:
        return wrap + "not found."
    elif status_code == http.HTTPStatus.UNAUTHORIZED:
        return "The token is not valid."
    elif status_code == http.HTTPStatus.FORBIDDEN:
        return wrap + "Reached request limit to the API."
    else:
        return wrap + "unknown error"


class Zenhub:
    def __init__(
            self,
            token,
            timeout=ZENHUB_DEFAULT_TIMEOUT,
    ):
        self.__authorizationHeader = {"X-Authentication-Token": token}
        self.__timeout = timeout

    def __get_releases(self, repo_id):
        resp = requests.get(ZENHUB_PATH_GET_RELEASES % repo_id, timeout=self.__timeout,
                            headers=self.__authorizationHeader)
        if resp.status_code != http.HTTPStatus.OK:
            return None, error(status_code=resp.status_code, wrap="zenhub get releases failed: %s" % resp.text)

        releases = json.loads(resp.text)

        return releases, ""

    def __add_or_remove_issue_from_release(self, release_id, issues):
        resp = requests.patch(ZENHUB_PATH_ADD_OR_REMOVE_ISSUE_FROM_RELEASE % release_id, timeout=self.__timeout,
                              headers=self.__authorizationHeader, json=issues)
        if resp.status_code != http.HTTPStatus.OK:
            return error(status_code=resp.status_code,
                         wrap="zenhub add or remove issue from release failed: %s" % resp.text)
        return ""

    def get_release_id_by_version(self, repo_id, version):
        releases, err = self.__get_releases(repo_id)
        if err != "":
            return None, err

        for r in releases:
            if r['title'] == version:
                return r['release_id'], ""

        return None, ""

    def add_release_to_issue(self, repo_id, release_id, issue_number):
        add_issues = {'add_issues': [{'repo_id': repo_id, 'issue_number': issue_number}], 'remove_issues': []}
        return self.__add_or_remove_issue_from_release(release_id, add_issues)

    def clean_releases_to_issue_except_by_milestone(self, repo_id, milestone, issue_number):
        releases, err = self.__get_releases(repo_id)
        if err != "":
            return err

        for r in releases:
            if r['state'] != 'open':
                continue

            if r['title'] == milestone:
                err = self.add_release_to_issue(repo_id, r['release_id'], issue_number)
                if err != "":
                    return err
            else:
                remove_issue = {'add_issues': [], 'remove_issues': [{'repo_id': repo_id, 'issue_number': issue_number}]}
                resp = requests.patch(ZENHUB_PATH_ADD_OR_REMOVE_ISSUE_FROM_RELEASE % r['release_id'],
                                      timeout=self.__timeout,
                                      headers=self.__authorizationHeader,
                                      json=remove_issue)
                if resp.status_code != http.HTTPStatus.OK:
                    return error(status_code=resp.status_code,
                                 wrap="zenhub add issue from release failed: %s" % resp.text)

        return ""

    def get_issue_data(self, repo_id, issue_number):
        resp = requests.get(ZENHUB_PATH_GET_ISSUE_DATA % (repo_id, issue_number), timeout=self.__timeout,
                            headers=self.__authorizationHeader)
        if resp.status_code != http.HTTPStatus.OK:
            return None, error(status_code=resp.status_code, wrap="zenhub get issue data failed: %s" % resp.text)

        issue_data = json.loads(resp.text)

        return issue_data, ""
