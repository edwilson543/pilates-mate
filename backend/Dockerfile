FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy over project metadata and install dependencies (but not project, to preserve dependency cache).
COPY uv.lock pyproject.toml ./
COPY deployment/entrypoint.sh ./
RUN uv sync --no-dev --no-install-project --locked

# Copy over project source code and install
COPY src ./src
ARG APP_VERSION
RUN echo '__version__ = "'${APP_VERSION}'"' > src/pilates/version.py
RUN uv pip install . --no-deps

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Add a non-root 'app' user to group 'app'.
RUN groupadd app
RUN useradd app -g app

# Make entrypoint script executable.
RUN chmod +x entrypoint.sh

# Transfer ownership of all files to the non-root user.
RUN chown -R app:app .

# Change user to the app user.
USER app

EXPOSE 8000
# U˙se the entrypoint script to decide which command is run.
ENTRYPOINT ["./entrypoint.sh"]
