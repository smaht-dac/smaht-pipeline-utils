.. _repo:

===============================
Pipeline's Repository Structure
===============================

To be picked up correctly by some of the commands, a repository needs to be set up as follow:

- A **descriptions** folder to store workflow description files (CWL and WDL).
- A **dockerfiles** folder to store Docker images.
  Each image should have its own subfolder with all the required components and the *Dockerfile*.
  Subfolder names will be used to tag the corresponding images together with the version from the VERSION file.
- A **portal_objects** folder to store the objects representing metadata for the pipeline.
  This folder should include several subfolders:
    - A **workflows** folder to store metadata for :ref:`Workflow <workflow>` objects as YAML files.
    - A **metaworkflows** folder to store metadata for :ref:`Pipeline <metaworkflow>` objects as YAML files.
    - A **file_format.yaml** file to store metadata for :ref:`File Format <file_format>` objects.
    - A **file_reference.yaml** file to store metadata for :ref:`File Reference <file_reference>` objects.
    - A **software.yaml** file to store metadata for :ref:`Software <software>` objects.
- A **PIPELINE** one line file with the pipeline name.
- A **VERSION** one line file with the pipeline version.

Example ``foo_bar`` pipeline:

::

    pipeline-foo_bar
    │
    ├── descriptions
    │   ├── foo.cwl
    │   └── bar.wdl
    │
    ├── dockerfiles
    │   │
    │   ├── image_foo
    │   │   ├── foo.sh
    │   │   └── Dockerfile
    │   │
    │   └── image_bar
    │       ├── bar.py
    │       └── Dockerfile
    │
    ├── portal_objects
    │   │
    │   ├── workflows
    │   │   ├── foo.yaml
    │   │   └── bar.yaml
    │   │
    │   ├── metaworkflows
    │   │   └── foo_bar.yaml
    │   │
    │   ├── file_format.yaml
    │   ├── file_reference.yaml
    │   └── software.yaml
    │
    ├── PIPELINE
    └── VERSION

Real examples can be found linked as submodules in our pipelines repository for SMaHT project here: https://github.com/smaht-dac/main-pipelines.
