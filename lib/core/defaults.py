#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org)
See the file 'LICENSE' for copying permission
"""

from lib.core.datatype import AttribDict

_defaults = {
    "csvDel": ',',
    "timeSec": 1,        # Reduced from 5 to 1 for faster time-based injections
    "googlePage": 1,
    "verbose": 1,
    "delay": 0,          # Keep at 0 for maximum speed
    "timeout": 10,       # Reduced from 30 to 10 for faster timeouts
    "retries": 1,        # Reduced from 3 to 1 for faster failure handling
    "csrfRetries": 0,
    "safeFreq": 0,
    "threads": 100,      # Increased from 1 to 100 for maximum parallelism
    "level": 1,
    "risk": 1,
    "dumpFormat": "CSV",
    "tablePrefix": "sqlmap",
    "technique": "BEUSTQ",
    "torType": "SOCKS5",
}

defaults = AttribDict(_defaults)
