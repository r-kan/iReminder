#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import cPickle
import errno
from cPickle import UnpicklingError
from util.global_def import debug, error


def load(pickle_file):
    """output: is_exist, value"""
    try:
        pickle_fd = open(pickle_file, "r")
    except IOError as err:
        if errno.ENOENT == err.errno:
            debug("cache file does not exist: %s" % pickle_file)
            return False, None
        assert False
    try:
        value = cPickle.load(pickle_fd)
        return True, value
    except (ValueError, UnpicklingError, EOFError):
        error("cannot read pickle file: %s, suggest re-fetch the pickle file" % pickle_file)
        assert False


def save(pickle_file, value):
    pickle_fd = open(pickle_file, "w")
    try:
        cPickle.dump(value, pickle_fd)
    except AttributeError as msg:
        error("fail to write cache %s" % str(msg))
    pickle_fd.close()
