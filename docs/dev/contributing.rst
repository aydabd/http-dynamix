============
Contributing
============

We welcome contributions to Http Dynamix! 
There are many ways to contribute, from improving the documentation, submitting 
bug reports and feature requests or writing code which can be incorporated into
the main project itself.

Local Development Installation
------------------------------

For developers or contributors:

.. code-block:: bash

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

Docker/Compose Test Execution
-----------------------------

You can run all tests in parallel using Docker Compose:

.. code-block:: bash

    docker compose up --build

To run only integration tests, override the command in compose.yaml:

.. code-block:: yaml

    command: ["pytest", "-n", "auto", "tests/test_clients_integration.py"]

This uses pytest-xdist for parallel execution. The Dockerfile and compose.yaml are set up for both CI and local testing.

Publish Documentation To Confluence
-----------------------------------

To publish the documentation to Confluence, you need to virtualenv python and
installed hatch. 
Then you need to set the following environment variables into `.env` file:

.. code-block:: bash

   CONFLUENCE_SERVER_USER=<your_confluence_user-at-server>
   CONFLUENCE_API_TOKEN=<your-api-token-for-confluence>

After that, you can run the following command to publish the documentation to Confluence:

.. code-block:: bash

   # Publish the documentation to Confluence
   hatch run release:all

.. note::

    Ensure your project is released with the version number before publishing the
    documentation to Confluence.


You can find the published documentation at the link provided in the output of 
the command.

For more information about documentation publishing, check the
``pyproject.toml`` file and ``docs/conf.py`` file.