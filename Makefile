.PHONY: run-dev
run-dev:
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 55000

.PHONY: run-prod
run-prod:
	@echo "Starting production server..."
	@if [ "$$(uname)" = "Darwin" ]; then \
		CPU_CORES=$$(sysctl -n hw.ncpu); \
	else \
		CPU_CORES=$$(grep -c ^processor /proc/cpuinfo); \
	fi; \
	echo "Detected $$CPU_CORES CPU cores. Configuring $$CPU_CORES workers..."; \
	gunicorn app.main:app --workers $$CPU_CORES --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:55000

.PHONY: remote-build
remote-build:
	@echo "Creating git tag..."
	@if [ -z "${VERSION}" ]; then \
		echo "VERSION variable is not set. Use 'make remote-build VERSION=x.y.z' to set the version."; \
		exit 1; \
	fi
	@git tag v${VERSION}
	@git push origin v${VERSION}
	@echo "Git tag v${VERSION} pushed. Remote build should be triggered by GitHub Actions."

.PHONY: remote-pull
remote-pull:
	@echo "Pulling Docker image..."
	@if [ -z "${VERSION}" ]; then \
		echo "VERSION variable is not set. Use 'make remote-pull VERSION=x.y.z' to set the version."; \
		exit 1; \
	fi
	@docker pull ghcr.io/ivanzhovannik/docsabot:v${VERSION}
	@echo "Docker image ghcr.io/ivanzhovannik/docsabot:v${VERSION} pulled successfully."
