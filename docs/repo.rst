====================
Repository structure
====================

To be picked up correctly by some of the commands, a repository needs to be set up as follows:

  - A **cwl** folder to store *cwl* and *workflow cwl* files.
  - A **dockerfiles** folder to store docker images.
    Each image should have its own folder with all the required components and the *Dockerfile*.
    The folder name will be used to tag the image together with the version from the VERSION file.
  - A **portal_objects** folder to store the objects representing metadata for the pipeline.
    This folder should include several subfolders:
      - A **workflows** folder to store metadata for Workflow objects as json files.
      - A **metaworkflows** folder to store metadata for MetaWorkflow objects as json files.
      - A **file_format.json** to store metadata for FileFormat objects.
      - A **file_reference.json** to store metadata for FileReference objects.
      - A **software.json** to store metadata for Software objects.
  - A **PIPELINE** file with the pipeline name.
  - A **VERSION** file with the pipeline version.

::

    Example foo_bar pipeline

    pipeline-foo_bar
    ├── cwl
    │   ├── foo.cwl
    │   └── bar.cwl
    ├── dockerfiles
    │   ├── image_foo
    │   │   ├── foo.sh
    │   │   └── Dockerfile
    │   └── image_bar
    │       ├── bar.sh
    │       └── Dockerfile
    ├── portal_objects
    │   ├── workflows
    │   │   ├── foo.json
    │   │   └── bar.json
    │   ├── metaworkflows
    │   │   └── foo_bar.json
    │   ├── file_format.json
    │   ├── file_reference.json
    │   └── software.json
    ├── PIPELINE
    └── VERSION
