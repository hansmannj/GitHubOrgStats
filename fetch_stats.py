import argparse
import csv
import json
from urllib.parse import parse_qs, urlparse

import requests


class OrgStats:

    def __init__(self, args, direct_params, indirect_params):
        self.args = args
        self.org = self.args.organization
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.args.github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.direct_params = direct_params
        self.indirect_params = indirect_params
        self.skipped_private = 0
        self.skipped_archived = 0
        self.processed = 0
        self.repo_list = []

    def read_stats(self):
        '''Reads the paginated stats for all pages for all repos and calls internal methods to
        store the data for later output.

        Raises:
            HTTPError:
                In case of exceptions when querying the GitHub API.
        '''

        print(
            f'Fetching statistics for '\
                f'{"public and private" if not self.args.skip_private else "only the public"}' \
                f' repositories of {self.org}. Archived repositories will be ' \
                    f'{"skipped" if self.args.skip_archived else "included"}...'
        )

        last_page = False
        page = 1
        while not last_page:
            try:
                response = requests.get(
                    f"https://api.github.com/orgs/{self.org}/repos?per_page=100&page={page}",
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("Something went wrong, details: " + str(e))

            resp_json = json.loads(response.content)
            self._read_stats_page(resp_json)
            page += 1
            # As the response might be paginated, repeating this until reaching the last page.
            # I assume, that the last page should not have a "next" in the link header or no link
            # header is present at all, probably if the response is not pagineted.
            # Some docu on pagination in GitHub API:
            # https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28
            if "link" in response.headers and not "next" in response.headers["link"]:
                last_page = True
            if not "link" in response.headers:
                last_page = True

        print(f"Processed {self.processed} repos in total. " \
              f"Skipped {self.skipped_private} private and {self.skipped_archived } " \
              "archived repos.")

    def _read_stats_page(self, page):
        '''Reads the stats for all repos on the passed page and stores the defined params in
        self.repo_list for later output"

        Args:
           page: str (JSON)
                JSON of the passed page to be processed
        '''

        for repo in page:
            self.processed += 1
            if self.args.skip_private and repo["private"]:
                print(f"Skipping private repo: {repo['name']}", end="\r")
                self.skipped_private += 1
                continue

            if self.args.skip_archived and repo["archived"]:
                print(f"Skipping archived repo: {repo['name']}", end="\r")
                self.skipped_archived += 1
                continue

            print(f"Processing repository: {repo['name']}", end="\r")
            repo_data = {}
            for param in self.direct_params:
                repo_data[param] = repo[param]

            for param in self.indirect_params:
                repo_data[param] = self._get_indirect_param_count(repo[f"{param}_url"])

            self.repo_list.append(repo_data)

    def write_csv(self):
        '''Writes self.repo_list a .csv file."
        '''
        with open(f"{self.org}_stats.csv", 'w', newline='') as stats_file:
            writer = csv.DictWriter(stats_file, self.repo_list[0].keys())
            writer.writeheader()
            writer.writerows(self.repo_list)

    def _get_indirect_param_count(self, param_url):
        '''Calculated the count for a parameter, which is not already directly included in the
        response of https://api.github.com/orgs/{self.org}/.
        For those parameters, a url is given, which needs to be requested and the number elements
        of the returned list of the paginated response represent the counter for this parameter.

        Args:
           param_url: str
                JSON of the passed page to be processed

        Returns:
            The counter for the given parameter

        Raises:
            HTTPError:
                In case of exceptions when querying the GitHub API.
        '''

        try:
            # the trick here is, that we add the query parameter per_page = 1.
            # Now we can try to get the count for our indirect parameter from the "last" link
            # in the link header.
            # However, there might be cases, where no link header or no last link in the link header
            # is present.
            # Guess that might be the case, when we have 0 or 1 elements in the returned list.
            # The link header is included also in HEAD requests.
            response = requests.head(f"{param_url}?per_page=1", headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Something went wrong, details: " + str(e))

        if "link" in response.headers:
            number = self._get_last_link_number(response.headers["link"])
            if number:
                return number

        try:
            # if no link header was present, or no "last" link in the link header, we will do a GET
            # instead of a HEAD request and check the returned list directly, instead of analyzing
            # the link header. The number of elements of the returned list should be the value for
            # the counter of the given indirect parameter.
            response = requests.get(param_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Something went wrong, details: " + str(e))

        resp_json = json.loads(response.content)
        return len(resp_json)

    def _get_last_link_number(self, link_header):
        '''Get the number of the link in the link header with rel=last.
        If no "last" link is found, None will be returned.

        Args:
           link_header: str
                value of the link header

        Returns:
            The number of the last link | None in case the "last" link does not
            exist.
        '''

        links = link_header.split(",")

        for link in links:
            if "last" in link:
                link = link.rsplit(";")[0]
                link = link.replace("<", "")
                link = link.replace(">", "")
                return parse_qs(urlparse(link).query)["page"][0]
            return None


def get_args():
    '''This function creates a command line arguments parser, adds arguments to it
    and returns the parsed arguments.

    Returns: argparse.Namespace object
    '''
    parser = argparse.ArgumentParser(
        description="This script scans through all repos of a given organization, " \
            "fetches several stats (stars, watchers, forks) and stores them to a csv file."
    )
    parser.add_argument("github_token", help="your personal github token.")
    parser.add_argument("organization", help="name of the github organization.")
    parser.add_argument("-p", "--skip_private", help="if set, private repos of the organization" \
        "will be skipped. Default: False, i.e. private repos will be included.",
        action="store_true", default=False)
    parser.add_argument("-a", "--skip_archived", help="if set, archived repos of the organization " \
        "will be skipped. Default: False, i.,e. archived repos will be included." \
            "repos.", action="store_true", default=False)
    args = parser.parse_args()

    return args


def main():
    args = get_args()
    DIRECT_PARAMS = [
        "id", "name", "full_name", "private", "archived", "stargazers_count", "forks_count"
    ]
    INDIRECT_PARAMS = ["subscribers"]  # those, that appear with a "_url" suffix in the JSON of
    # https://api.github.com/users/ORGANIZATION_NAME/repos

    org_stats = OrgStats(args, DIRECT_PARAMS, INDIRECT_PARAMS)
    org_stats.read_stats()
    org_stats.write_csv()


if __name__ == '__main__':
    main()
