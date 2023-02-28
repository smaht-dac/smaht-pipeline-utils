<img src="https://github.com/dbmi-bgm/cgap-pipeline/blob/master/docs/images/cgap_logo.png" width="200" align="right">

# CGAP Pipeline Utilities

Utilities for CGAP pipeline.

For more information on available commands and how to contribute and deploy pipelines within CGAP infrastructure check the extended [*documentation*](https://cgap-pipeline-utils.readthedocs.io/en/latest/ "cgap-pipeline-utils documentation").

## Install

The software is python based. To install the software and the required packages, we recommend using a fresh virtual environment.
Please refer to `pyproject.toml` for the supported Python versions.

The package is available on [*pypi*](https://pypi.org/project/cgap-pipeline-utils "cgap-pipeline-utils pypi"):

    pip install cgap-pipeline-utils

To install from source:

    git clone https://github.com/dbmi-bgm/cgap-pipeline-utils.git
    cd cgap-pipeline-utils
    make configure
    make update
    make build

To check that the software is correctly installed, try to run `pipeline_utils`. If installed from source, this command may fail with a bash “command not found” error, try `poetry run pipeline_utils` instead.

See `make info` for details on make targets.
