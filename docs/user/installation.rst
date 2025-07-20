============
Installation
============

This section covers different installation methods for http-dynamix.

Requirements
------------

- Python 3.12+
- Docker (for container-based usage)

Local Installation In Virtual Environment Via Pip
-------------------------------------------------

.. code-block:: bash
    
    # Install mamba-githook for creation of isolated virtual environment.
    #Choose the correct installer for your platform(linux-amd64, linux-arm64, windows-amd64, windows-arm64)
    curl -L https://github.com/aydabd/mamba-githook/releases/download/1.0.1/mamba-githook-installer-linux-arm64 \
        -o mamba-githook-installer && \
        chmod +x mamba-githook-installer && \
        ./mamba-githook-installer install
    
    # Install micromamba via mamba-githook
    mamnba-githook install-micromamba
    # Activate permanent micromamba in your shell, Then you need to restart your shell
    mamba-githook init-shell

    # Create virtual environment via micromamba
    micromamba create -n http-dynamix-api-tests-env python=3.12

    # Activate virtual environment
    micromamba activate http-dynamix-api-tests-env

    # Install package via pip
    pip install http-dynamix

    # Check installation
    micromamba list http-dynamix

Docker/Compose Installation and Testing
---------------------------------------

You can use Docker Compose to build and test the project in a containerized environment:

.. code-block:: bash

    docker compose up --build

To run only integration tests, override the command in compose.yaml:

.. code-block:: yaml

    command: ["pytest", "-n", "auto", "tests/test_clients_integration.py"]

Dependencies
------------

Dependencies will be installed automatically when installing the package via pip or when building the Docker image.

Core Dependencies
^^^^^^^^^^^^^^^^^

- `httpx`_
- `loguru`_
- `pytest`_

.. _`httpx`: https://www.python-httpx.org/
.. _`loguru`: https://loguru.readthedocs.io/en/stable/
.. _`pytest`: https://docs.pytest.org/en/stable/
