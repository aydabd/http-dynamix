# Dockerfile for build micromamba:2.0.5 with pytest and pytest-asyncio
FROM mambaorg/micromamba:2.0.5

WORKDIR /app

# Copy files
COPY --chown=$MAMBA_USER:$MAMBA_USER docs/examples/tests /app/tests

# Install dependencies
RUN micromamba install -y -n base -c conda-forge \
    pip pytest pytest-xdist pytest-asyncio && \
    micromamba clean --all --yes

# Activate env inside container for RUN command
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Install package
RUN pip install http-dynamix

# Run tests
ENTRYPOINT ["pytest", "/tests"]
