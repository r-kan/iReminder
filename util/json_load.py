#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""load setting from previous created files (currently only support read json format)"""

from __future__ import print_function
import json
from util.global_def import error


class JsonLoader(object):

    def __init__(self, in_file):
        self.__fd = open(in_file)
        try:
            self.__json_data = json.load(self.__fd)
        except ValueError as e:
            error("[json] json syntax error \"%s\"" % in_file)
            error(str(e))
            import sys
            sys.exit()

    def __del__(self):
        self.__fd.close()

    def get_root_obj(self, pattern):
        assert isinstance(self.__json_data, dict)
        if pattern in self.__json_data:
            return self.__json_data[pattern]
        return None

    def get_json_data(self):
        return self.__json_data


def print_json(data):
    if isinstance(data, dict):
        for key in data:
            if type(data[key]) in [dict, list]:
                print_json(data[key])
            else:
                print(key, "=>", data[key])
    elif isinstance(data, list):
        for entry in data:
            print_json(entry)
    else:
        print(data)


if __name__ == '__main__':
    with open('image.json') as json_data:
        d = json.load(json_data)
        json_data.close()
        print_json(d)
