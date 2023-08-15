#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from os.path import join, dirname
from io import open


setup(
    name="ChecklistTools",
    version="0.1.0",
    description=(
        "A collection of Python scripts to facilitate work with "
        "ENA sample checklists"
    ),
    long_description=open(
        join(dirname(__file__), "README.rst"), encoding="utf-8"
    ).read(),
    py_modules=["helpers", "validate_samples"],
    install_requires=["pandera>=0.16"],
    entry_points={
        "console_scripts": [
            "validate_samples = validate_samples:main"
        ]
    },
    author="Markus Englund",
    author_email="markus.englund@nbis.se",
    url="https://github.com/jmenglund/ChecklistTools",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    keywords=["ENA", "checklist", "validation", "sample metadata", "pandera", "pandas"],
)
