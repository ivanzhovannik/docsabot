from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import openai
import os
import git
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

app = FastAPI()

class UpdateDocsRequest(BaseModel):
    diff: str
    repo: str
    docs_path: str = "docs"  # Default to 'docs' if not provided
    model: str = "gpt-3.5-turbo"  # Default model
    temperature: float = Field(1, ge=0, le=2)  # Default temperature with constraints

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

@app.post("/update-docs")
async def update_docs(request: UpdateDocsRequest):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        raise HTTPException(status_code=400, detail="GitHub token is required")

    diff = request.diff
    repo_url = f"https://{github_token}@github.com/{request.repo}"

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, request.repo.split('/')[-1])
        
        try:
            # Clone the repository
            repo = git.Repo.clone_from(repo_url, repo_path)

            docs_dir = os.path.join(repo_path, request.docs_path)
            if not os.path.exists(docs_dir):
                raise HTTPException(status_code=404, detail="Docs directory not found")

            # Find all text-based documentation files
            doc_files = []
            for root, _, files in os.walk(docs_dir):
                for file in files:
                    if file.endswith(('.md', '.txt')):
                        doc_files.append(os.path.join(root, file))

            # Process files in parallel using a threadpool
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(process_file, file, diff, request.model, request.temperature): file
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Documentation updated and changes pushed"}
