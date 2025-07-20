# Repository Guidelines

This project uses **Hatch** and **mamba-githook** for development tasks and environment management.

## Environment Setup

Before submitting changes, ensure you have installed mamba-githook and micromamba:

```bash
# Install mamba-githook
curl -L https://github.com/aydabd/mamba-githook/releases/download/1.0.1/mamba-githook-installer-linux-amd64 \
    -o mamba-githook-installer && \
chmod +x mamba-githook-installer && \
./mamba-githook-installer install

# Install micromamba via mamba-githook
mamba-githook install-micromamba
# Activate permanent micromamba in your shell
mamba-githook init-shell

# Create and activate the environment using the shared environment spec
micromamba create -n http-dynamix-env -f .githooks.d/pre-commit_environment.yml -y
micromamba activate http-dynamix-env
```

## Pre-commit and CI Checks

Before committing, activate the environment and run:

```bash
micromamba activate http-dynamix-env
hatch run pre-release:all
```

This command executes formatting, static type checks, tests with coverage, and documentation builds. Ensure it passes without errors before committing.

The CI pipeline uses the same mamba-githook and micromamba setup with `.githooks.d/pre-commit_environment.yml` to ensure consistency between local and CI environments.


