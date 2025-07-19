# Dockerfile for build micromamba:2.0.5 with pytest and pytest-asyncio
FROM mambaorg/micromamba:latest

WORKDIR /app

# Copy files
COPY --chown=$MAMBA_USER:$MAMBA_USER docs/examples/tests /app/tests
COPY --chown=$MAMBA_USER:$MAMBA_USER src /app/src
COPY --chown=$MAMBA_USER:$MAMBA_USER pyproject.toml /app/pyproject.toml
COPY --chown=$MAMBA_USER:$MAMBA_USER .git /app/.git

# Install dependencies
RUN micromamba install -y -n base -c conda-forge \
    pip pytest pytest-xdist pytest-asyncio git hatch && \
    micromamba clean --all --yes

# Activate env inside container for RUN command
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Install package
RUN pip install -e .

# Run tests
ENTRYPOINT ["pytest", "tests"]
