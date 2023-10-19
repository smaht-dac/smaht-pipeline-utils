.. _install:

=======
Install
=======

PyPI
^^^^

The package is available on pypi_:

.. _pypi: https://pypi.org/project/smaht-pipeline-utils

.. code-block:: bash

    pip install smaht-pipeline-utils

Source
^^^^^^

The version on pypi may be outdated or may not be the required version.
To install the latest version from source:

.. code-block:: bash

    git clone https://github.com/smaht-dac/smaht-pipeline-utils.git
    cd smaht-pipeline-utils
    make configure
    make update
    make build

Please refer to `pyproject.toml <https://github.com/smaht-dac/smaht-pipeline-utils/blob/main/pyproject.toml>`_ for the supported Python version.
