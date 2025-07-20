==========
Quickstart
==========

This guide helps you get started with Http Dynamix.

Prerequisites
-------------

- Docker installed and running

Basic Setup with Docker Compose (Recommended)
---------------------------------------------

1. Create test directory:

.. code-block:: bash

   mkdir test-api-service && cd test-api-service

2. create pytest.ini:

.. literalinclude:: ../examples/tests/pytest.ini
   :caption: pytest.ini
   :linenos:

3. Create pytest test cases:

.. literalinclude:: ../examples/tests/test_httpbin_org_service.py
   :language: python
   :caption: test_httpbin_org_service.py
   :linenos:

4. Create compose.yaml:

.. literalinclude:: ../examples/compose.yaml
   :language: yaml
   :caption: compose.yaml
   :linenos:

5. Run all tests in parallel:

.. code-block:: bash

   docker compose up --build

6. To run only integration tests, override the command in compose.yaml:

.. code-block:: yaml

   command: ["pytest", "-n", "auto", "tests/test_clients_integration.py"]

This uses pytest-xdist for parallel execution. The Dockerfile and compose.yaml are set up for both CI and local testing.
