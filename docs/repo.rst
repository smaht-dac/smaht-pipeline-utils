.. _repo:

====================
Repository structure
====================

To be picked up correctly by some of the commands, a repository needs to be set up as follows:

  - A **descriptions** folder to store *cwl* and *wdl* workflow description files.
  - A **dockerfiles** folder to store docker images.
    Each image should have its own folder with all the required components and the *Dockerfile*.
    The folder name will be used to tag the image together with the version from the VERSION file.
  - A **portal_objects** folder to store the objects representing metadata for the pipeline.
    This folder should include several subfolders:
      - A **workflows** folder to store metadata for Workflow objects as yaml files.
      - A **metaworkflows** folder to store metadata for MetaWorkflow objects as yaml files.
      - A **file_format.yaml** to store metadata for FileFormat objects.
      - A **file_reference.yaml** to store metadata for FileReference objects.
      - A **software.yaml** to store metadata for Software objects.
  - A **PIPELINE** file with the pipeline name.
  - A **VERSION** file with the pipeline version.

::

    Example foo_bar pipeline

    pipeline-foo_bar
    ├── descriptions
    │   ├── foo.cwl
    │   └── bar.wdl
    ├── dockerfiles
    │   ├── image_foo
    │   │   ├── foo.sh
    │   │   └── Dockerfile
    │   └── image_bar
    │       ├── bar.py
    │       └── Dockerfile
    ├── portal_objects
    │   ├── workflows
    │   │   ├── foo.yaml
    │   │   └── bar.yaml
    │   ├── metaworkflows
    │   │   └── foo_bar.yaml
    │   ├── file_format.yaml
    │   ├── file_reference.yaml
    │   └── software.yaml
    ├── PIPELINE
    └── VERSION
