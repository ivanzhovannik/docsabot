## Sample Usage in GitHub Actions

```yaml
name: Update Documentation

on:
  pull_request:
    types: [closed]
    branches: [main]

jobs:
  update-docs:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get PR diff
        id: diff
        run: git diff HEAD^ HEAD > diff.txt

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GHCR_PAT }}

      - name: Pull Docsabot Docker image
        run: docker pull ghcr.io/ivanzhovannik/docsabot:latest

      - name: Run Docsabot container
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          docker run --rm \
          -e OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }} \
          -e GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }} \
          -v ${{ github.workspace }}:/workspace \
          ghcr.io/ivanzhovannik/docsabot:latest \
          curl -X POST http://localhost:55000/ai/update-docs \
          -H "Content-Type: application/json" \
          -d @- <<EOF
          {
            "diff": "$(cat /workspace/diff.txt)",
            "repo": "${{ github.repository }}",
            "docs_path": "docs",
            "model": "gpt-3.5-turbo",
            "temperature": 1.0
          }
          EOF
```

Do not forget to create `config/.secrets.yaml`:

```yaml
---
openai:
    api_key: sk--your-key

github:
    token: gh-your-token
```

