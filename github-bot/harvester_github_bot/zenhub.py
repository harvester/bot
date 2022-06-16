import requests
import http
import json

ZENHUB_DEFAULT_BASE_URL = "https://api.zenhub.com"
ZENHUB_DEFAULT_TIMEOUT = 15

ZENHUB_PATH_GET_RELEASES = ZENHUB_DEFAULT_BASE_URL + "/p1/repositories/%d/reports/releases"
ZENHUB_PATH_ADD_ISSUE_FROM_RELEASE = ZENHUB_DEFAULT_BASE_URL + "/p1/reports/release/%s/issues"


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

    def get_release_id_by_version(self, repo_id, version):
        resp = requests.get(ZENHUB_PATH_GET_RELEASES % repo_id, timeout=self.__timeout,
                            headers=self.__authorizationHeader)
        if resp.status_code != http.HTTPStatus.OK:
            return None, error(status_code=resp.status_code, wrap="zenhub get releases failed: %s")

        releases = json.loads(resp.text)
        for r in releases:
            if r['title'] == version:
                return r['release_id'], ""

        return None, ""

    def add_release_to_issue(self, repo_id, release_id, issue_number):
        add_issues = {'add_issues': [{'repo_id': repo_id, 'issue_number': issue_number}], 'remove_issues': []}
        resp = requests.patch(ZENHUB_PATH_ADD_ISSUE_FROM_RELEASE % release_id, timeout=self.__timeout,
                              headers=self.__authorizationHeader, json=add_issues)
        if resp.status_code != http.HTTPStatus.OK:
            return error(status_code=resp.status_code, wrap="zenhub add issue from release failed:")
        return ""
