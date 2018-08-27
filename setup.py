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

setup(
    name='mmdzanata',
    version='0.1',
    packages=['mmdzanata'],
    url='',
    license='MIT',
    author='Stephen Gallagher',
    author_email='sgallagh@redhat.com',
    description='Tools for working with translations of modulemd',
    install_requires=[
        'click',
        'koji',
        'requests',
        'babel',
    ],
    entry_points={
        'console_scripts': ['mmdzanata=mmdzanata.cli:cli'],
    },
)
