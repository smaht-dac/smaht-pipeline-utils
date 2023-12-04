# SMaHT Portal Pipeline Utilities

Utilities for deploying pipelines and interfacing with SMaHT portal infrastructure.

For more information on available commands and how to contribute and deploy pipelines within the infrastructure check the extended [*documentation*](https://smaht-pipeline-utils.readthedocs.io/en/latest/ "smaht-pipeline-utils documentation").

## Install

The software is python based. To install the software and the required packages, we recommend using a fresh virtual environment.
Please refer to `pyproject.toml` for the supported Python versions.

The package is available on [*pypi*](https://pypi.org/project/smaht-pipeline-utils "smaht-pipeline-utils pypi"):

    pip install smaht-pipeline-utils

To install from source:

    git clone https://github.com/smaht-dac/smaht-pipeline-utils.git
    cd smaht-pipeline-utils
    make configure
    make update
    make build

To check that the software is correctly installed, try to run `smaht_pipeline_utils`. If installed from source, this command may fail with a bash “command not found” error, try `poetry run smaht_pipeline_utils` instead.

See `make info` for details on make targets.
