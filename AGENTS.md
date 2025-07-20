# Repository Guidelines

This project uses **Hatch** and **micromamba** for development tasks and environment management. For local shell integration, you may optionally use **mamba-githook**.

## Environment Setup

### Local Development

You can use micromamba directly, or optionally mamba-githook for shell integration:

```bash
# Install micromamba (recommended)
curl -L https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xvj -C ~/bin
export PATH=~/bin:$PATH

# Or install mamba-githook for shell integration (optional)
curl -L https://github.com/aydabd/mamba-githook/releases/download/1.0.1/mamba-githook-installer-linux-amd64 \
    -o mamba-githook-installer && \
chmod +x mamba-githook-installer && \
./mamba-githook-installer install
mamba-githook install-micromamba
mamba-githook init-shell

# Create and activate the environment using the shared environment spec
micromamba create -n http-dynamix-env -f .githooks.d/pre-commit_environment.yml -y
micromamba activate http-dynamix-env
```

### CI Setup

The CI pipeline uses the official [setup-micromamba](https://github.com/mamba-org/setup-micromamba) GitHub Action and patches the environment file for the correct Python version:

```yaml
- name: Patch environment file for Python version
  run: |
    sed -i 's/- python/- python=${{ matrix.python-version }}/' .githooks.d/pre-commit_environment.yml
    sed -i 's/^name: .*/name: http-dynamix-env/' .githooks.d/pre-commit_environment.yml
- name: Setup micromamba
  uses: mamba-org/setup-micromamba@v2
  with:
    environment-file: .githooks.d/pre-commit_environment.yml
    environment-name: http-dynamix-env
- name: Run pre-release checks
  shell: bash -el {0}
  run: hatch run pre-release:all
```

## Pre-commit and CI Checks

Before committing, activate the environment and run:

```bash
micromamba activate http-dynamix-env
hatch run pre-release:all
```

This command executes formatting, static type checks, tests with coverage, and documentation builds. Ensure it passes without errors before committing.

The CI pipeline uses the same micromamba environment spec to ensure consistency between local and CI environments.


