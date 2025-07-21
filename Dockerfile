# syntax=docker/dockerfile:1

# Dockerfile for HTTP Dynamix project
# This Dockerfile sets up a micromamba environment with necessary dependencies
# and runs pre-release tests using Hatch.

FROM mambaorg/micromamba:latest

WORKDIR /app

# Copy files
COPY --chown=$MAMBA_USER:$MAMBA_USER . /app/

# Install dependencies
RUN micromamba install -y -n base -c conda-forge \
    git hatch pandoc && \
    micromamba clean --all --yes

# Activate env inside container for RUN command
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Run tests in parallel by default inside micromamba environment
ENTRYPOINT ["micromamba", "run", "-n", "base"]
CMD ["hatch", "run", "pre-release:all"]
