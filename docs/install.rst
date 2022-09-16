=============
Quick Install
=============

The package is available on pypi_:

.. _pypi: https://pypi.org/project/cgap-pipeline-utils

.. code-block:: bash

    pip install cgap-pipeline-utils

Note however that the version on pypi may be outdated or may not be
the required version. To install the latest version from source:

.. code-block:: bash

    git clone https://github.com/dbmi-bgm/cgap-pipeline-utils.git
    cd cgap-pipeline-utils
    make configure
    make update
    make build
