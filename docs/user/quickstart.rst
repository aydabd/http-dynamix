==========
Quickstart
==========

This guide helps you get started with Http Dynamix.

Prerequisites
-------------

- Docker installed and running

Basic Setup with Docker Compose(Recommended)
--------------------------------------------

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

. Create compose.yaml:

.. literalinclude:: ../examples/compose.yaml
   :language: yaml
   :caption: compose.yaml
   :linenos:

4. Run docker compose:

.. code-block:: bash

   docker compose run -it --rm http-dynamix-api-service-tests:latest
