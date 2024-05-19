# Automated Documentation Update Script

This script automates the process of fetching the latest commit from a specified GitHub repository, retrieving the diff for that commit, and then using an API to update documentation based on the diff.

## Prerequisites
- A valid GitHub token set as an environment variable `GITHUB_TOKEN`.
- The Docsabot API running locally or accessible via a specified URL.

## Usage
1. Set your GitHub token.
2. Configure the repository details and branch.
3. Run the script to fetch the latest commit's diff and send it to Docsabot for processing.

The script handles API communications and logs each step to ensure you can track the process and any potential issues.

```python
import requests
import os
import json

# GitHub details
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is not set.")
print("GitHub token retrieved successfully.")

REPO_OWNER = 'your-repo-owner'
REPO_NAME = 'your-repo-name'
BRANCH = 'main'
print(f"Repository: {REPO_OWNER}/{REPO_NAME}, Branch: {BRANCH}")

# OpenAI API URL
api_url = "http://localhost:55000/ai/update-docs"
print(f"OpenAI API URL: {api_url}")

# Headers for the GitHub API request
gh_headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}
print("GitHub headers set.")

# Get the latest commit on the main branch
commit_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{BRANCH}'
print(f"Fetching latest commit from URL: {commit_url}")
commit_response = requests.get(commit_url, headers=gh_headers)
print(f"GitHub API response status: {commit_response.status_code}")
commit_data = commit_response.json()
latest_commit_sha = commit_data['sha']
print(f"Latest commit SHA: {latest_commit_sha}")

# Get the diff for the latest commit
diff_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{latest_commit_sha}'
print(f"Fetching diff from URL: {diff_url}")
diff_response = requests.get(diff_url, headers=gh_headers)
print(f"GitHub API diff response status: {diff_response.status_code}")
diff = diff_response.text
print(f"Diff: {diff}")

# Headers for the Docsabot API request
headers = {
    "Content-Type": "application/json",
}
print("Docsabot headers set.")

# Payload for the Docsabot API request
payload = {
    "diff": diff,
    "repo": f"{REPO_OWNER}/{REPO_NAME}",
    "docs_path": "docs",
    "model": "gpt-3.5-turbo",
    "temperature": 1.0
}
print(f"Payload for Docsabot: {json.dumps(payload, indent=2)}")

# Make the API request to Docsabot to update docs
print(f"Making request to Docsabot API at {api_url}")
response = requests.post(api_url, headers=headers, data=json.dumps(payload))
print(f"Docsabot API response status: {response.status_code}")
print(f"Docsabot API response: {response.json()}")
```