#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This file is part of modulemd-zanata
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

import os
import gi
import click
import requests
import mmdtranslations
from babel.messages import Catalog, pofile

gi.require_version('Modulemd', '1.0')
from gi.repository import Modulemd


@click.command()
@click.option('-b', '--branch', default="rawhide", type=str,
              help="The distribution release (Default: rawhide)",
              metavar="<branch_name>")
@click.option('-z', '--zanata-rest-url',
              default="https://fedora.zanata.org/rest",
              type=str, help="""
The Zanata URL
(Default: https://fedora.zanata.org/)
""",
              metavar="<zanata_project>")
@click.option('-p', '--zanata-project', default="fedora-modularity-translations",
              type=str, help="""
The Zanata project
(Default: fedora-modularity-translations)
""",
              metavar="<zanata_project>")
@click.option("-v", "--zanata-project-version", default="f29",
              type=str, help="""
The project version.
(Default: f29)
""", metavar="[f28, f29, ...]")
@click.option('-c', '--zanata-user-config', default=None,
              type=click.Path(exists=True, readable=True),
              help="""
Path to the user config for Zanata. (Default: ~/.config/zanata.ini)
""")
def main(branch, zanata_rest_url, zanata_project,
         zanata_project_version, zanata_user_config):
    """
    Extract translations from all modules included in a particular version of
    Fedora or EPEL.
    """
    k = mmdtranslations.get_koji_session()
    script_dir = os.path.dirname(os.path.realpath(__file__))

    if branch == "rawhide":
        branch = mmdtranslations.get_rawhide_version(k)

    tags = mmdtranslations.get_tags_for_branch(branch)

    tagged_builds = []
    for tag in tags:
        tagged_builds.extend(mmdtranslations.get_latest_modules_in_tag(k, tag))

    # Make the list unique since some modules may have multiple tags
    unique_builds = {}
    for build in tagged_builds:
        unique_builds[build['id']] = build

    catalog = mmdtranslations.get_module_catalog(k, unique_builds)

    with open("fedora-modularity-translations.pot", mode="wb") as f:
        pofile.write_po(f, catalog, sort_by_file=True)


if __name__ == "__main__":
    main()
