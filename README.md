# Stargazer

Stargazer is a Python script that fetches information about users who have starred a specific GitHub repository. Importantly, it finds the email addresses of the gazers of a repo, in case you'd like to do some targeted marketing. 

## Prerequisites

- Python 3.6+
- `requests` library (install with `pip install requests`)

## Setup

1. Clone this repository or download the `stargazer.py` file.

2. Install the required library:
   ```
   pip install requests
   ```

3. (Optional) Set up a GitHub Personal Access Token:
   - Create a token at https://github.com/settings/tokens
   - Set it as an environment variable:
     ```
     export GITHUB_TOKEN=your_token_here
     ```

## Usage

Run the script from the command line with the following syntax:
python stargazer.py owner/repo [--token YOUR_GITHUB_TOKEN]

- Replace `owner/repo` with the GitHub repository you want to analyze (e.g., `microsoft/vscode`).
- The `--token` argument is optional if you've set the `GITHUB_TOKEN` environment variable.

Example:
```
python stargazer.py microsoft/vscode --token ghp_your_token_here
```

Providing your gh_token will allow you to make more requests before getting rate limited by Github.