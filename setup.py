#!/usr/bin/env python

from setuptools import setup, find_packages

# Description
with open('README.md') as fd:
    long_description = fd.read()
#end with

# Requirements
with open('requirements.txt') as fr:
    set_parsed = fr.read().splitlines()
#end with

# Set requires
install_requires = [req.strip() for req in set_parsed]
tests_requires = [
    'pytest'
]

setup(
    name='cgap-pipeline-utils',
    version=open('VERSION').readlines()[-1].rstrip(),
    description = 'Collection of utilities for cgap-pipeline',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Michele Berselli, Phil Grayson',
    author_email = 'berselli.michele@gmail.com',
    url='https://github.com/dbmi-bgm/cgap-pipeline-utils',
    include_package_data=True,
    packages=['pipeline_utils'],
    classifiers=[
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3'
            ],
    entry_points = {
        'console_scripts': [
            'pipeline_utils = pipeline_utils.__main__:main',
        ]
    },
    install_requires=install_requires,
    setup_requires=install_requires,
    tests_require=tests_requires,
    python_requires = '>=3.6, <3.8',
    license = 'MIT'
)
