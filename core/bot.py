import os
import logging
import tempfile
import traceback
import git
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.schema import DocumentUpdate, UpdateDocsPayload, OpenAIMessage, OpenAIMessageQuery
from config.config import settings

logger = logging.getLogger(__name__)

def create_openai_messages(diff: str, old_content: str, repo_summary: str) -> OpenAIMessageQuery:
    messages = [
        OpenAIMessage(role="system", content="You are a documentation assistant. Your goal is to update documentation files based on the changes. Only include the actual documentation, no explanations about generation is needed."),
        OpenAIMessage(role="user", content=f"Here is a summary of the repository:\n{repo_summary}"),
        OpenAIMessage(role="user", content=f"Here is the diff for the latest commit:\n{diff}"),
        OpenAIMessage(role="user", content=f"Here is the current content of the document:\n{old_content}"),
        OpenAIMessage(role="assistant", content="Please update the document based on the diff and the repository context.")
    ]
    return OpenAIMessageQuery(messages=messages)

def process_file(client, file_path, diff, model, temperature, repo_summary) -> DocumentUpdate:
    with open(file_path, "r") as f:
        old_content = f.read()

    messages = create_openai_messages(diff, old_content, repo_summary)

    logger.debug(f"Using Client: {client} of type {type(client)}")
    updated_content = client.chat.completions.create(
        model=model,
        messages=[message.model_dump() for message in messages.messages],
        max_tokens=1500,
        temperature=temperature
    )

    logger.debug(f"Received Response: {updated_content}")
    new_message = updated_content.choices[0].message
    try:
        new_message = OpenAIMessage.model_validate(new_message.model_dump())
    except:
        logger.error(f"Content Message parsing was unsuccessful: {traceback.format_exc()}")

    logger.debug(f"Assistant's message: {new_message}")

    with open(file_path, "w") as f:
        f.write(new_message.content)

    return DocumentUpdate(path=file_path, old_content=old_content, new_content=new_message.content)

def generate_repo_summary(repo_path: str) -> str:
    repo_summary = []
    for root, dirs, files in os.walk(repo_path):
        level = root.replace(repo_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        repo_summary.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            repo_summary.append(f"{subindent}{f}")
    return "\n".join(repo_summary)

def create_pull_request(repo: git.Repo, branch_name: str, base_branch: str, token: str, repo_owner: str, repo_name: str):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": "Docsabot Documentation Update",
        "head": branch_name,
        "base": base_branch,
        "body": "Automated documentation updates by Docsabot."
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        logger.info("Pull request created successfully.")
    else:
        logger.error(f"Failed to create pull request: {response.status_code} {response.text}")

def update_docs(client, payload: UpdateDocsPayload) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, payload.repo.split('/')[-1])

        # Clone the repository
        repo = git.Repo.clone_from(payload.repo, repo_path)

        repo_summary = generate_repo_summary(repo_path)

        docs_dir = os.path.join(repo_path, payload.docs_path)
        if not os.path.exists(docs_dir):
            raise FileNotFoundError("Docs directory not found")

        # Find all text-based documentation files
        doc_files = []
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(('.md', '.txt', '.plantuml', '.puml')):
                    doc_files.append(os.path.join(root, file))

        logger.debug(f"Found documentation files: {doc_files}")

        updates: list[DocumentUpdate] = []
        # Process files in parallel using a threadpool
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(process_file, client, file, payload.diff, payload.model, payload.temperature, repo_summary): file
                for file in doc_files
            }
            for future in as_completed(futures):
                file = futures[future]
                try:
                    update = future.result()
                    updates.append(update)
                    logger.info(f"Updated file: {update.path}")
                except Exception as exc:
                    logger.error(f"File {file} generated an exception: {exc}\n{traceback.format_exc()}")

        payload.updates = updates

        # Create a new branch and push the changes
        latest_commit_sha = repo.head.commit.hexsha
        new_branch = f"docsabot-docs-update-{latest_commit_sha[:8]}"
        repo.git.checkout(b=new_branch)
        repo.git.add(update=True)
        repo.index.commit("Update documentation")
        origin = repo.remote(name='origin')
        origin.push(refspec=f"{new_branch}:{new_branch}")

        # Create a pull request
        create_pull_request(repo, new_branch, "main", settings.GITHUB.TOKEN, payload.repo.split('/')[-2], payload.repo.split('/')[-1])

    return "Documentation updated and pull request created."
