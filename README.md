# GitHubOrgStats

This is a simply and not fully tested script to extract some stats for a github organization, such
as number of starts, watchers, forks, etc.
It will store the results in a .csv file, which can be imported in spread sheets for visualisation.

The script has not been fully tested and comes without any warranties. Use at your own risk.

Usage:

```bash
python3 fetch_stats.py YOUR_GITHUB_TOKEN YOUR_ORGANIZATION_NAME
```

It will store the results in a .csv file with headers:
`id, name, full_name, private, stargazers_count, watchers_count, forks_count`

To install all necessary dependencies and a venv for this project, run `make setup` initially.
