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