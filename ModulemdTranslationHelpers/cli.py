# -*- coding: utf-8 -*-
# This file is part of ModulemdTranslationHelpers
# Copyright (C) 2018-2019 Stephen Gallagher
#
# Fedora-License-Identifier: MIT
# SPDX-2.0-License-Identifier: MIT
# SPDX-3.0-License-Identifier: MIT
#
# This program is free software.
# For more information on the license, see COPYING.
# For more information on free software, see
# <https://www.gnu.org/philosophy/free-sw.en.html>.

from __future__ import print_function

import click
import gi
import os
import os.path
import logging
import xmlrpc.client
import Utils
import Fedora

from babel.messages import pofile

gi.require_version('Modulemd', '2.0')  # noqa
from gi.repository import Modulemd


##############################################################################
# Common options for all commands                                            #
##############################################################################


@click.group()

@click.option('--debug/--no-debug', default=False)

@click.option('-k', '--koji-url',
              default=Fedora.KOJI_URL,
              type=str, help="The URL of the Koji build system.",
              show_default=True,
              metavar="<URL>")

@click.option('-b', '--branch', default="rawhide", type=str,
              help="The distribution release",
              metavar="<branch_name>")

@click.pass_context
def cli(ctx, debug, branch, koji_url):
    """Tools for managing modularity translations."""

    ctx.obj = dict()
    if debug:
      logging.basicConfig(level=logging.DEBUG)

    ctx.obj['session'] = xmlrpc.client.ServerProxy(koji_url)

    ctx.obj['branch'] = branch

    if branch == "rawhide":
        ctx.obj['branch'] = Fedora.get_fedora_rawhide_version(ctx.obj['session'])

##############################################################################
# Subcommands                                                                #
##############################################################################

##############################################################################
# `ModulemdTranslationHelpers extract`                                       #
##############################################################################


@cli.command()

@click.option('-p', '--pot-file',
              default='fedora-modularity-translations.pot',
              type=click.File(mode='wb', atomic=True, lazy=True),
              show_default=True,
              metavar="<PATH>",
              help="Path to the portable object template (POT) file to hold "
                   "the translatable strings.")

@click.option('--project-name',
              default='fedora-modularity-translations',
              show_default=True,
              help='Name of the project.')

@click.pass_context
def extract(ctx, pot_file, project_name):
    """
    Extract translatable strings from modules.
    Extract translations from all modules included in a particular version of
    Fedora or EPEL.
    """
    index = Utils.get_index_from_tags(
      ctx.parent.obj['session'], Fedora.get_tags_for_fedora_branch(
        ctx.parent.obj['branch']))

    catalog = Utils.get_translation_catalog_from_index(index, project_name)
    pofile.write_po(pot_file, catalog, sort_by_file=True)

    print("Wrote extracted strings for %s to %s" % (ctx.obj['branch'],
                                                    pot_file.name))


##############################################################################
# `ModulemdTranslationHelpers generate_metadata`                             #
##############################################################################

@cli.command()

@click.option('-d', '--pofile-dir',
              default='.',
              help="Path to a directory containing portable object (.po) "
                   "translation files",
              type=click.Path(exists=True, dir_okay=True, resolve_path=True,
                              readable=True))

@click.option('-y', '--yaml-file',
              default='fedora-modularity-translations.yaml',
              type=click.File(mode='wb', atomic=True, lazy=True),
              show_default=True,
              metavar="<PATH>",
              help="Path to the YAML file to hold the modified modulemd-index containing"
                   "the translated strings.")

@click.pass_context
def generate_metadata(ctx, pofile_dir, yaml_file):
    """
    Add translations to modulemd-index inplace.
    :return: 0 on successful creation of modulemd-translation,
    nonzero on failure.
    """
    index = Utils.get_index_from_tags(
      ctx.parent.obj['session'], Fedora.get_tags_for_fedora_branch(
        ctx.parent.obj['branch']))

    # Process all .po files in the provided directory
    translation_files = [f for f in os.listdir(pofile_dir) if
                         os.path.isfile((os.path.join(pofile_dir, f))) and
                         f.endswith(".po")]

    catalogs = list()
    for f in translation_files:
      with open(f, 'r') as infile:
        catalog = pofile.read_po(infile)
        catalogs.append(catalog)

    Utils.get_modulemd_translations_from_catalog(catalogs, index)
    yaml_file.write(index.dump_to_string().encode('utf-8'))
    print("Wrote modified modulemd-index YAML to %s" % yaml_file.name)


if __name__ == "__main__":
    cli(obj={})