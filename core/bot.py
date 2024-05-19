import os
import tempfile
import git
import openai
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_file(file_path, diff, model, temperature):
    with open(file_path, "r") as f:
        content = f.read()
    
    # Simulating an OpenAI completion request
    updated_content = openai.Completion.create(
        engine=model,
        prompt=f"Update the following documentation based on these changes: {diff}\n\n{content}",
        max_tokens=1500,
        temperature=temperature
    )

    with open(file_path, "w") as f:
        f.write(updated_content.choices[0].text)

    return file_path

def update_docs(diff, repo_url, docs_path, model, temperature):
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
                if file.endswith(('.md', '.txt')):
                    doc_files.append(os.path.join(root, file))

        # Process files in parallel using a threadpool
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(process_file, file, diff, model, temperature): file
                for file in doc_files
            }
            for future in as_completed(futures):
                file = futures[future]
                try:
                    result = future.result()
                    print(f"Updated file: {result}")
                except Exception as exc:
                    print(f"File {file} generated an exception: {exc}")

        # Commit and push the changes
        repo.git.add(update=True)
        repo.index.commit("Update documentation")
        origin = repo.remote(name='origin')
        origin.push()

    return "Documentation updated and changes pushed"
