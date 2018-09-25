#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This file is part of ModulemdTranslationHelpers
# Copyright (C) 2018 Stephen Gallagher
#
# Fedora-License-Identifier: MIT
# SPDX-2.0-License-Identifier: MIT
# SPDX-3.0-License-Identifier: MIT
#
# This program is free software.
# For more information on the license, see COPYING.
# For more information on free software, see
# <https://www.gnu.org/philosophy/free-sw.en.html>.

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ModulemdTranslationHelpers',
    version='0.2',
    packages=['ModulemdTranslationHelpers'],
    url='https://github.com/fedora-modularity/ModulemdTranslationHelpers',
    license='MIT',
    author='Stephen Gallagher',
    author_email='sgallagh@redhat.com',
    description='Tools for working with translations of modulemd',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # ModulemdTranslationHelpers also requires koji and libmodulemd which
    # are not available on PyPI and must be installed separately. On Fedora,
    #  this is done with `dnf install koji libmodulemd`
    install_requires=[
        'click',
        'requests',
        'babel',
    ],
    entry_points={
        'console_scripts': [
            'ModulemdTranslationHelpers=ModulemdTranslationHelpers.cli:cli'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    include_package_data=True,
)
