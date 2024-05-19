import os
import logging
import tempfile
import traceback
import git
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def process_file(client, file_path, diff, model, temperature):
    with open(file_path, "r") as f:
        content = f.read()
    
    # Simulating an OpenAI completion request
    logger.debug(f"Using Client: {client} of type {type(client)}")
    updated_content = client.chat.completions.create(
        engine=model,
        prompt=f"Update the following documentation based on these changes: {diff}\n\n{content}",
        max_tokens=1500,
        temperature=temperature
    )
    print(updated_content)

    with open(file_path, "w") as f:
        f.write(updated_content.choices[0].text)

    return file_path

def update_docs(client, diff, repo_url, docs_path, model, temperature):
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, repo_url.split('/')[-1])

        # Clone the repository
        repo = git.Repo.clone_from(repo_url, repo_path)

        docs_dir = os.path.join(repo_path, docs_path)
        if not os.path.exists(docs_dir):
            raise FileNotFoundError("Docs directory not found")

        # Find all text-based documentation files
        doc_files = []
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(('.md', '.txt', '.plantuml', '.puml')):
                    doc_files.append(os.path.join(root, file))
        print(doc_files)

        # Process files in parallel using a threadpool
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(process_file, client, file, diff, model, temperature): file
                for file in doc_files
            }
            for future in as_completed(futures):
                file = futures[future]
                try:
                    result = future.result()
                    print(f"Updated file: {result}")
                except Exception as exc:
                    print(f"File {file} generated an exception: {exc}\n{traceback.format_exc()}")

        # Commit and push the changes
        repo.git.add(update=True)
        repo.index.commit("Update documentation")
        origin = repo.remote(name='origin')
        origin.push()

    return "Documentation updated and changes pushed"
