# -*- coding: utf-8 -*-
# This file is part of modulemd-zanata
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

from __future__ import print_function

import requests

KOJI_URL = 'https://koji.fedoraproject.org/kojihub'


def get_fedora_rawhide_version(session, debug=False):
    # Koji sometimes disconnects for no apparent reason. Retry up to 5
    # times before failing.
    for attempt in range(5):
        try:
            build_targets = session.getBuildTargets('rawhide')
        except requests.exceptions.ConnectionError:
            if debug:
                print("Connection lost while retriving rawhide branch, "
                      "retrying...",
                      file=sys.stderr)
        else:
            # Succeeded this time, so break out of the loop
            break

    return build_targets[0][
        'build_tag_name'].partition('-build')[0]


def get_tags_for_fedora_branch(branch):
    return ['%s-modular' % branch,
            '%s-modular-override' % branch,
            '%s-modular-pending' % branch,
            '%s-modular-signing-pending' % branch,
            '%s-modular-updates' % branch,
            '%s-modular-updates-candidate' % branch,
            '%s-modular-updates-pending' % branch,
            '%s-modular-updates-testing' % branch,
            '%s-modular-updates-testing-pending' % branch]
