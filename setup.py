#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='yoi',
    version='0.0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        # FIXME - read requirements.txt!
    ],
)

