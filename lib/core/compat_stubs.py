#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org)
See the file 'LICENSE' for copying permission
"""

"""
Compatibility stubs for removed extra modules (beep, cloak)
This module provides minimal replacements for functionality from the removed extra/ directory
to maintain core SQLMap functionality while reducing package size.
"""

import os

def beep():
    """
    Stub replacement for beep functionality from extra.beep.beep
    No-op implementation since beep is not essential for core functionality
    """
    pass

def decloak(filepath):
    """
    Stub replacement for decloak functionality from extra.cloak.cloak
    Returns the file content as-is since cloak/decloak is not essential for basic operation
    This assumes that files were not actually cloaked or are already decloaked
    """
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except IOError:
        return b""