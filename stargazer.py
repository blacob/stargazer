import requests
import csv
import time
import os
import argparse
from datetime import datetime, timezone

# GitHub repo details
owner = ''  # Replace with the GitHub repo owner
repo = ''  # Replace with the repo name
url = f'https://api.github.com/repos/{owner}/{repo}/stargazers'
gh_token = os.getenv('GITHUB_TOKEN')
headers = {
    'Accept': 'application/vnd.github.v3.star+json',
    'Authorization': 'token ' + gh_token
}
csv_filename = 'gazers.csv'

def get_last_processed():
    try:
        with open(csv_filename, mode='r') as file:
            lines = file.readlines()
            if len(lines) > 1:
                last_line = lines[-1].strip().split(',')
                return int(last_line[2]), last_line[0], last_line[3]
    except FileNotFoundError:
        pass
    return 1, None, None

def initialize_csv():
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Username', 'Email', 'Page', 'Starred_At'])

def get_user_repos(username):
    repos_url = f'https://api.github.com/users/{username}/repos'
    repos_response = requests.get(repos_url, headers=headers, params={'per_page': 100})
    return repos_response.json()

def get_first_commit(username, repo_name):
    commits_url = f'https://api.github.com/repos/{username}/{repo_name}/commits'
    commits_response = requests.get(commits_url, headers=headers, params={'per_page': 1})
    commits_data = commits_response.json()
    if isinstance(commits_data, list) and len(commits_data) > 0:
        return commits_data[0]['sha']
    return None

def get_email_from_patch(username, repo_name, commit_sha):
    patch_url = f'https://github.com/{username}/{repo_name}/commit/{commit_sha}.patch'
    patch_response = requests.get(patch_url, headers=headers)
    if patch_response.status_code == 200:
        patch_content = patch_response.text
        start_index = patch_content.find('From:')
        if start_index != -1:
            end_index = patch_content.find('>', start_index)
            email = patch_content[start_index + 6:end_index]
            if email and "noreply" not in email.lower():
                return email
    return None

def find_user_email(username):
    repos_data = get_user_repos(username)
    for repo in repos_data:
        if not repo['fork']:
            repo_name = repo['name']
            commit_sha = get_first_commit(username, repo_name)
            if commit_sha:
                email = get_email_from_patch(username, repo_name, commit_sha)
                if email:
                    return email
    return None

def save_user_data(username, email, page, starred_at):
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, email, page, starred_at])

def process_stargazers(owner, repo, gh_token=None):
    url = f'https://api.github.com/repos/{owner}/{repo}/stargazers'
    headers = {
        'Accept': 'application/vnd.github.v3.star+json'
    }
    if gh_token:
        headers['Authorization'] = f'token {gh_token}'
    
    initialize_csv()
    last_page, last_username, last_starred_at = get_last_processed()
    page = last_page

    while True:
        response = requests.get(url, headers=headers, params={'per_page': 100, 'page': page})
        data = response.json()

        if len(data) == 0:
            print("No more stargazers to process.")
            break

        for star in data:
            user = star['user']
            username = user['login']
            starred_at = star['starred_at']
            
            if last_starred_at and starred_at <= last_starred_at:
                continue

            print(f"Processing {username} (starred at {starred_at}) on page {page}...")
            email = find_user_email(username)

            if email:
                print(f"Found email: {email}")
            else:
                print(f"No email found for {username}")

            save_user_data(username, email, page, starred_at)
            print(f"Saved data for {username}")

        time.sleep(1)
        print(f"Page {page} processed and saved to {csv_filename}.")
        page += 1

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process stargazers for a GitHub repository.')
    parser.add_argument('repo', help='GitHub repository in the format owner/repo')
    parser.add_argument('--token', help='GitHub personal access token (optional)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    owner, repo = args.repo.split('/')
    gh_token = args.token or os.getenv('GITHUB_TOKEN')

    process_stargazers(owner, repo, gh_token)