import argparse
import csv
import json

import requests


class OrgStats:

    def __init__(self):
        self.repo_list = []

    def read_page_stats(self, resp_json):
        for repo in resp_json:
            repo_data = {}
            repo_data["id"] = repo["id"]
            repo_data["name"] = repo["name"]
            repo_data["full_name"] = repo["full_name"]
            repo_data["private"] = repo["private"]
            repo_data["stargazers_count"] = repo["stargazers_count"]
            repo_data["watchers_count"] = repo["watchers_count"]
            repo_data["forks_count"] = repo["forks_count"]

            self.repo_list.append(repo_data)

    def write_csv(self, filename="org_stats.csv"):
        with open(filename, 'w', newline='') as stats_file:
            writer = csv.DictWriter(stats_file, self.repo_list[0].keys())
            writer.writeheader()
            writer.writerows(self.repo_list)


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
    args = parser.parse_args()

    return args


def main():
    args = get_args()
    token = args.github_token
    org = args.organization
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    org_stats = OrgStats()

    last_page = False
    page = 1
    while not last_page:
        try:
            response = requests.get(
                f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Something went wrong, details: " + str(e))

        resp_json = json.loads(response.content)
        org_stats.read_page_stats(resp_json)
        page += 1
        if not "next" in response.headers["link"]:
            last_page = True

    org_stats.write_csv()


if __name__ == '__main__':
    main()
