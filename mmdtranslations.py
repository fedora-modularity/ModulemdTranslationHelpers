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

import gi
import koji

from babel.messages import Catalog

gi.require_version('Modulemd', '1.0')
from gi.repository import Modulemd


def get_koji_session():
    return koji.ClientSession('https://koji.fedoraproject.org/kojihub')


def get_rawhide_version(session):
    return session.getBuildTargets('rawhide')[0]['build_tag_name'].partition('-build')[0]


def get_tags_for_branch(branch):
    return ['%s-modular' % branch,
            '%s-modular-override' % branch,
            '%s-modular-pending' % branch,
            '%s-modular-signing-pending' % branch,
            '%s-modular-updates' % branch,
            '%s-modular-updates-candidate' % branch,
            '%s-modular-updates-pending' % branch,
            '%s-modular-updates-testing' % branch,
            '%s-modular-updates-testing-pending' % branch]


def get_latest_modules_in_tag(session, tag):
    tagged = session.listTagged(tag, latest=False)

    # Find the latest, in module terms.  Pungi does this.
    # Collect all contexts that share the same NSV.
    NSVs = {}
    for entry in tagged:
        name, stream = entry['name'], entry['version']
        version = entry['release'].rsplit('.', 1)[0]

        NSVs[name] = NSVs.get(name, {})
        NSVs[name][stream] = NSVs[name].get(stream, {})
        NSVs[name][stream][version] = NSVs[name][stream].get(version, [])
        NSVs[name][stream][version].append(entry)

    latest = []
    for name in NSVs:
        for stream in NSVs[name]:
            version = sorted(list(NSVs[name][stream].keys()))[-1]
            latest.extend(NSVs[name][stream][version])

    return latest


def get_module_catalog(session, builds):
    catalog = Catalog(project="fedora-modularity-translations")

    for build_id in builds.keys():
        build = session.getBuild(build_id)
        print("Processing %s:%s" % (build['package_name'], build['nvr']))

        module_stream = "%s:%s" % (
            build['extra']['typeinfo']['module']['name'],
            build['extra']['typeinfo']['module']['stream'])

        modulemds = Modulemd.objects_from_string(
            build['extra']['typeinfo']['module']['modulemd_str'])

        # We should only get a single modulemd document from Koji
        assert len(modulemds) == 1

        mmd = modulemds[0]

        # Process the summary
        msg = catalog.get(mmd.props.summary)
        if msg:
            locations = msg.locations
        else:
            locations = []
        locations.append(("%s;%s;summary" % (
                mmd.props.name,mmd.props.stream), 1))
        catalog.add(mmd.props.summary, locations=locations)

        # Process the description
        msg = catalog.get(mmd.props.description)
        if msg:
            locations = msg.locations
        else:
            locations = []
        locations.append(("%s;%s;description" % (
            mmd.props.name, mmd.props.stream), 2))
        catalog.add(mmd.props.description, locations=locations)

        # Get any profile descriptions
        for profile_name, profile in modulemds[0].peek_profiles().items():
            if profile.props.description:
                msg = catalog.get(profile.props.description)
                if msg:
                    locations = msg.locations
                else:
                    locations = []

                locations.append(("%s;%s;profile;%s" % (
                    mmd.props.name,
                    mmd.props.stream,
                    profile.props.name),
                                       3))
                catalog.add(profile.props.description, locations=locations)

    return catalog