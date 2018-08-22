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

import click
import gi
import requests
import sys

import mmdtranslations

from babel.messages import pofile
from io import BytesIO

gi.require_version('Modulemd', '1.0')
from gi.repository import Modulemd


# name;stream;summary 0
# name;stream;description 1
# name;stream;profile;profilename 2


@click.command()
@click.option('-d', '--debug', default=False, is_flag= True,
              help="Add debugging output")
@click.option('-z', '--zanata-rest-url',
              default="https://fedora.zanata.org/rest",
              type=str, help="""
The Zanata URL
(Default: https://fedora.zanata.org/rest)
""",
              metavar="<zanata_rest_url>")
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
@click.option("-f", "--zanata-translation-file",
              default="fedora-modularity-translations",
              type=str, help="""
The name of the translated file in Zanata.
(Default: fedora-modularity-translations)
""")
def main(debug, zanata_rest_url, zanata_project,
         zanata_translation_file, zanata_project_version):
    """
    :param zanata_rest_url: The base URL to the zanata instance
    :param zanata_project: The project slug
    :param zanata_project_version: The version of the project
    :param zanata_translation_file: The translated file in Zanata
    :return: 0 on successful creation of modulemd-translation,
    nonzero on failure.
    """

    # Get the statistics on the translation project for this version
    stats_url = zanata_rest_url + "/stats/proj/%s/iter/%s" % (
        zanata_project, zanata_project_version)

    r = requests.get(stats_url, headers={"Accept": "application/json"})
    if r.status_code != 200:
        print("Project '%s:%s' does not exist." % (zanata_project,
                                                   zanata_project_version),
              file=sys.stderr)
        sys.exit(1)

    statistics = r.json()['stats']

    # We will pull down information for any locale that is at least partially
    # translated
    translated_locales = [t["locale"]
                          for t in statistics
                          if t["translated"] > 0]

    catalogs = dict()
    for loc in translated_locales:
        # Get the translation data for this locale
        pofile_url = zanata_rest_url +\
                     "/file/translation/%s/%s/%s/po?docId=%s" % (
                         zanata_project, zanata_project_version, loc,
                         zanata_translation_file)
        r = requests.get(pofile_url,
                         headers={"Accept": "application/octet-stream"})
        if r.status_code != 200:
            print("Could not retrieve translations for %s" % loc,
                  file=sys.stderr)
            continue

        if debug:
            print(r.text)

        # Read the po file into a catalog, indexed by the locale
        catalogs[loc] = pofile.read_po(
            BytesIO(r.content),
            domain="fedora-modularity-translations")

    translations = mmdtranslations.get_modulemd_translations_from_catalog_dict(
        catalogs)

    if debug:
        for translation in translations:
            print(translation.dumps())

    Modulemd.dump(sorted(translations), "modulemd-translations.yaml")





if __name__ == "__main__":
    main()
