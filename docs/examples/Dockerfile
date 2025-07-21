# syntax=docker/dockerfile:1
FROM mambaorg/micromamba:latest

WORKDIR /app

# Copy files
COPY --chown=$MAMBA_USER:$MAMBA_USER tests/pytest.ini /app/pytest.ini

# Install dependencies
RUN micromamba install -y -n base -c conda-forge \
    python pytest pytest-xdist pytest-asyncio && \
    micromamba clean --all --yes

# Activate env inside container for RUN command
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Install package
RUN pip install http-dynamix

# Run tests in parallel by default inside micromamba environment
ENTRYPOINT ["micromamba", "run", "-n", "base"]
CMD ["pytest", "-n", "auto", "tests"]