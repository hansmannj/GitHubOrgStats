# GitHubOrgStats

This is a simple and not fully tested script to extract some statistics for all repositories
belonging to a github organization, such as number of stars, watchers, forks, etc.
(Private or archived repositories can optionally be skipped).
It will store the results in a .csv file, which can be imported in spread sheets for visualisation.
:warning: The script has not been fully tested and comes without any warranties. Use at your own
risk.

## Initial setup

To install the necessary dependencies (assuming you already have pipenv and Python 3.9 installed),
run:

```bash
make setup
```

To configure the parameters, that should be extracted for the repos of your organization, adapt the
lists `primary_params` and `secondary_params` in `main()`.

- `primary_params` in this context are parameters, whose values are directly contained in the JSON
response of `https://api.github.com/orgs/ORGANIZATION_NAME/repos`.
- `secondary_params` are some of those, for which no value is given in the JSON, but instead a url, which
can be queried. Only tested so far with `subscribers_url`. The length of the list returned when querying this URL will
represent the count of `subscribers` in this case.

Initially I was not sure, why `stargazers_count` and `watchers_count` had the same numbers, and the
number of `watchers` did not seem to be correct. The documentation on this clarified things:
https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#starring-versus-watching :wink:

## Usage

The script must be called with as in the following:

```bash
python3 fetch_stats.py YOUR_GITHUB_TOKEN YOUR_ORGANIZATION_NAME
```

There are two optional flags, which can be set:

```bash
python3 fetch_stats.py YOUR_GITHUB_TOKEN YOUR_ORGANIZATION_NAME --public_only --non_archived_only
```

If `-p` or `--skip_private` is set, private repos of the organization will be skipped. The default
value is `False`, i.e. private repositories will be included by default.

Likewise, if `-n` or `--skip_archived` is set, archived repos of the organization will be skipped.
The default is `false`, i.e. archived repositories will be included by dedault.

The fetched stats will be written to a file `ORGANIZATION_NAME_stats.csv` including a header.
