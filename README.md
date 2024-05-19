# DocsaBot

DocsaBot is an automated documentation updating tool designed to streamline the process of maintaining accurate and up-to-date project documentation. It integrates directly with GitHub, using OpenAI to generate documentation updates based on changes in the codebase.

## Requirements

To run DocsaBot, you'll need Docker and Make. The required Python packages are listed in `requirements.txt`.

## Setup

1. Clone the repository.
2. Navigate to the cloned directory.
3. Build the Docker image using:

```shell
docker build -t docsabot .
```

## Usage

You can start the application in development or production mode:

- **Development Mode**

```shell
make run-dev
```

- **Production Mode**

```shell
make run-prod
```
### Usage examples

Some examples can be found in `docs/usage`

## Deployment

Deployments can be triggered via GitHub Actions, leveraging the `remote-build` target in the Makefile.

## License

This project is open-source under the MIT license. You are free to use, modify, and distribute the software as you see fit. No warranty is provided, and the original authors bear no liability for the use of this software.

---

For more detailed information and configuration, please refer to the provided Dockerfile, Makefile, and settings within the `config/` directory.
