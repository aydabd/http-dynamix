# Http Dynamix

[![Ruff Code Quality Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://docs.astral.sh/ruff/)
[![Documentation Built by Sphinx](https://img.shields.io/badge/Documentation-Built%20with%20Sphinx-blue?logo=read-the-docs&logoColor=white)](https://www.sphinx-doc.org)
[![Project Built with Hatchling](https://img.shields.io/badge/Project-Built%20with%20Hatchling-green?logo=python)](https://hatch.pypa.io/latest/)

Library for creating dynamic HTTP requests in puthon

## Quick Start

This guide helps you get started with Http Dynamix.

## Prerequisites

- Docker installed and running

## Basic Setup with Docker Compose (Recommended)

1.  Create test directory:

``` bash
mkdir -p test-api-service/tests && cd test-api-service
```

2.  create pytest configuration file <span class="title-ref">pytest.ini</span> in the <span class="title-ref">tests</span> directory:

<div class="literalinclude" caption="pytest.ini" linenos="">

../examples/tests/pytest.ini

</div>

3.  Create pytest test cases in \`tests/test_httpbin_org_service.py\`:

<div class="literalinclude" language="python" caption="test_httpbin_org_service.py" linenos="">

../examples/tests/test_httpbin_org_service.py

</div>

4.  Create compose.yaml:

<div class="literalinclude" language="yaml" caption="compose.yaml" linenos="">

../examples/compose.yaml

</div>

5.  Run all tests in parallel:

``` bash
docker compose up --build
```

6.  To run only specified tests, override the command in compose.yaml:

``` yaml
command: ["pytest", "-n", "auto", "tests/test_httpbin_org_service.py"]
```

This uses pytest-xdist for parallel execution.

## Contributing

We welcome contributions to Http Dynamix!
There are many ways to contribute, from improving the documentation, submitting
bug reports and feature requests or writing code which can be incorporated into
the main project itself.

## Local Development Installation

For developers or contributors:

``` bash
# Install mamba-githook for creation of isolated virtual environment, 
# Choose the correct installer for your platform
# Supported: linux-amd64, linux-arm64, windows-amd64, windows-arm64
curl -L https://github.com/aydabd/mamba-githook/releases/download/1.0.1/mamba-githook-installer-linux-arm64 \
    -o mamba-githook-installer && \
    chmod +x mamba-githook-installer && \
    ./mamba-githook-installer install

# Install micromamba via mamba-githook
mamnba-githook install-micromamba
# Activate permanent micromamba in your shell, Then you need to restart your shell
mamba-githook init-shell

# Create virtual environment via micromamba
micromamba create -n http-dynamix-env hatch pandoc

# Activate virtual environment
micromamba activate http-dynamix-env

# Clone repository
git clone ssh://git@github.com:aydabd/http-dynamix.git
cd http-dynamix

# Install development dependencies
# This will install all dependencies from pyproject.toml
hatch env create

# Run hatch for pre-release:all environment
hatch run pre-release:all

# Install the package in editable mode inside the micromamba environment
pip install -e .

# Build documentation in HTML format
hatch run pre-release:docs-html
```

## Docker/Compose Test Execution

You can run all tests in parallel using Docker Compose:

``` bash
docker compose up --build
```

To run only integration tests, override the command in compose.yaml:

``` yaml
command: ["pytest", "-n", "auto", "tests/test_clients_integration.py"]
```

This uses pytest-xdist for parallel execution. The Dockerfile and compose.yaml are set up for both CI and local testing.

## Publish Documentation To Confluence

To publish the documentation to Confluence, you need to virtualenv python and
installed hatch.
Then you need to set the following environment variables into <span class="title-ref">.env</span> file:

``` bash
CONFLUENCE_SERVER_USER=<your_confluence_user-at-server>
CONFLUENCE_API_TOKEN=<your-api-token-for-confluence>
```

After that, you can run the following command to publish the documentation to Confluence:

``` bash
# Publish the documentation to Confluence
hatch run release:all
```

> [!NOTE]
> Ensure your project is released with the version number before publishing the
> documentation to Confluence.

You can find the published documentation at the link provided in the output of
the command.

For more information about documentation publishing, check the
`pyproject.toml` file and `docs/conf.py` file.
