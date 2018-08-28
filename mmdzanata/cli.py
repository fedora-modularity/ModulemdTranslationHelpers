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
import koji
import mmdzanata
import mmdzanata.fedora
import os
import subprocess
import sys
import shutil

from babel.messages import pofile
from tempfile import TemporaryDirectory

gi.require_version('Modulemd', '1.0')
from gi.repository import Modulemd


##############################################################################
# Common options for all commands                                            #
##############################################################################


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('-k', '--koji-url',
              default=mmdzanata.fedora.KOJI_URL,
              type=str, help="The URL of the Koji build system.",
              show_default=True,
              metavar="<URL>")
@click.option('-b', '--branch', default="rawhide", type=str,
              help="The distribution release",
              metavar="<branch_name>")
@click.option('-z', '--zanata-url',
              default=mmdzanata.fedora.ZANATA_URL,
              type=str, help="The Zanata URL",
              show_default=True,
              metavar="<zanata_project>")
@click.option('-p', '--zanata-project',
              default=mmdzanata.fedora.ZANATA_PROJECT,
              type=str, help="The Zanata project",
              show_default=True,
              metavar="<zanata_project>")
@click.option('-f', '--zanata-translation-document',
              default=mmdzanata.fedora.ZANATA_DOCUMENT,
              help="The name of the translated file in Zanata.",
              show_default=True,
              metavar="<translation_document>")
@click.option('-c', '--zanata-user-config',
              default=lambda: "%s/.config/zanata.ini" % (
                      os.environ.get("HOME", '~')),
              help="Path to the Zanata User Config INI file",
              type=click.Path(exists=True))
@click.pass_context
def cli(ctx, debug, branch, koji_url, zanata_url, zanata_project,
        zanata_translation_document, zanata_user_config):

    ctx.obj = dict()
    ctx.obj['debug'] = debug

    ctx.obj['session'] = koji.ClientSession(koji_url)

    ctx.obj['branch'] = branch

    if branch == "rawhide":
        ctx.obj['branch'] = mmdzanata.fedora.get_fedora_rawhide_version(
            ctx.obj['session'])

    ctx.obj['zanata_url'] = zanata_url
    ctx.obj['zanata_project'] = zanata_project
    ctx.obj['zanata_translation_document'] = zanata_translation_document
    ctx.obj['zanata_user_config'] = zanata_user_config

##############################################################################
# Subcommands                                                                #
##############################################################################

##############################################################################
# `mmdzanata extract`                                                        #
##############################################################################


@cli.command()
@click.option('--upload/--no-upload', default=False,
              help='Whether to automatically push extracted strings to '
              'Zanata',
              show_default=True)
@click.pass_context
def extract(ctx, upload):
    """
    Extract translations from all modules included in a particular version of
    Fedora or EPEL.
    """

    catalog = mmdzanata.get_module_catalog_from_tags(
        ctx.parent.obj['session'], mmdzanata.fedora.get_tags_for_fedora_branch(
            ctx.parent.obj['branch']),
        debug=ctx.parent.obj['debug'])

    with TemporaryDirectory() as tdir:
        po_basename = "%s.pot" % ctx.parent.obj['zanata_translation_document']
        potfile = "%s/%s" % (tdir, po_basename)

        with open(potfile, mode="wb") as f:
            pofile.write_po(f, catalog, sort_by_file=True)

        # Optionally upload the extracted strings directly to Zanata
        if upload:
            # Use the zanata-cli to upload the pot file
            # It would be better to use the REST API directly here, but the XML
            # payload format is not documented.

            # First ensure that the requested branch exists in Zanata
            zanata_args = [
                '/usr/bin/zanata-cli', '-B', '-e', 'put-version',
                '--url', ctx.parent.obj['zanata_url'],
                '--version-project', ctx.parent.obj['zanata_project'],
                '--version-slug', ctx.parent.obj['branch'],
                '--user-config', ctx.parent.obj['zanata_user_config']
            ]
            result = subprocess.run(zanata_args, capture_output=True)
            if result.returncode or ctx.parent.obj['debug']:
                print(result.stderr.decode('utf-8'))
                print(result.stdout.decode('utf-8'))
            if result.returncode:
                sys.exit(1)

            # Update the translatable strings for this branch
            zanata_args = [
                '/usr/bin/zanata-cli', '-B', '-e', 'push',
                '--url', ctx.parent.obj['zanata_url'],
                '--project', ctx.parent.obj['zanata_project'],
                '--project-type', 'gettext',
                '--project-version', ctx.parent.obj['branch'],
                '--src-dir', tdir,
                '--user-config', ctx.parent.obj['zanata_user_config']
            ]
            result = subprocess.run(zanata_args, capture_output=True)
            if result.returncode or ctx.parent.obj['debug']:
                print(result.stderr.decode('utf-8'))
                print(result.stdout.decode('utf-8'))
            if result.returncode:
                sys.exit(2)

            print("Uploaded translatable strings for %s to Zanata" % (
                ctx.parent.obj['branch']))

        else:
            # Move the temporary path to the current directory
            shutil.move(potfile, po_basename)
            print("Wrote extracted strings for %s to %s" % (ctx.obj['branch'],
                                                            po_basename))


##############################################################################
# `mmdzanata generate_metadata`                                              #
##############################################################################

@cli.command()
@click.pass_context
def generate_metadata(ctx):
    """
    :return: 0 on successful creation of modulemd-translation,
    nonzero on failure.
    """

    zanata_rest_url = "%s/rest" % ctx.parent.obj['zanata_url']

    translations = mmdzanata.get_modulemd_translations(
        zanata_rest_url,
        ctx.parent.obj['zanata_project'],
        ctx.parent.obj['branch'],
        ctx.parent.obj['zanata_translation_document'],
        ctx.parent.obj['debug']
    )

    translation_file = "%s-%s.yaml" % (
        ctx.parent.obj['zanata_translation_document'],
        ctx.parent.obj['branch'])

    Modulemd.dump(sorted(translations), translation_file)

    print("Wrote modulemd-translations YAML to %s" % translation_file)


if __name__ == "__main__":
    cli(obj={})
