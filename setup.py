#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This file is part of mmdzanata
# Copyright (C) 2017-2018 Stephen Gallagher
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
    name='mmdzanata',
    version='0.4',
    packages=['mmdzanata', 'mmdzanata.fedora'],
    url='https://github.com/sgallagher/modulemd-zanata',
    license='MIT',
    author='Stephen Gallagher',
    author_email='sgallagh@redhat.com',
    description='Tools for working with translations of modulemd',
    long_description=long_description,
    # mmdzanata also requires koji, libmodulemd and zanata-client which are not
    # available on PyPI and must be installed separately. On Fedora, this is
    # done with `dnf install koji libmodulemd zanata-client`
    install_requires=[
        'click',
        'requests',
        'babel',
    ],
    entry_points={
        'console_scripts': ['mmdzanata=mmdzanata.cli:cli'],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ),
)
