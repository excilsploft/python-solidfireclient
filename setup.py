#!/usr/bin/env python

import setuptools


with open('requirements.txt') as f:
        required = f.read().splitlines()

setuptools.setup(
    setup_requires=['d2to1'],
    d2to1=True,
    install_requires=required)
