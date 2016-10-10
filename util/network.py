#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import urllib2
from util.global_def import get_accessible_pivot


def check_access_status():
    print("check network connection...")
    try:
        urllib2.urlopen(get_accessible_pivot(), timeout=3)
        print("status: connected")
        return True
    except urllib2.URLError:
        pass
    print("status: not connected")
    return False


__CHECKED = False
__REACHABLE = False


def reachable():
    global __CHECKED, __REACHABLE
    if not __CHECKED:
        __REACHABLE = check_access_status()
        __CHECKED = True
    return __REACHABLE


if __name__ == '__main__':
    print(reachable())
