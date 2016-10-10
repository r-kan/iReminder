#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os
from base.setting.utility import Rank, RANK_KEY
from util.global_def import warning
from util.json_load import JsonLoader

import sys
reload(sys)
sys.setdefaultencoding('UTF8')  # need this for str(pattern_of_type_unicode) can work

ATTRIBUTE_KEY = "attribute"
LOCATION_KEY = "location"


class Image(object):

    def __init__(self, pattern, group_name=None, ranks=None, attributes=None, option=None, size=None, location=None):
        self.pattern = str(pattern)  # raw pattern is of type 'unicode'
        self.group_name = group_name
        self.ranks = ranks
        self.attributes = attributes
        self.option = option
        self.size = size
        self.location = location

    def print(self):
        print(self.pattern)
        for rank in self.ranks:
            rank.print()
        for key in self.attributes:
            attribute_values = []
            for attribute_value in self.attributes[key]:
                attribute_values.append(attribute_value)
            print('\t', key, "=>", *attribute_values)
        if self.location:
            print('\t', self.location)

    @staticmethod
    def create(pattern, data, group_name, option, size, global_rank):
        assert isinstance(data, dict)
        ranks = []
        attributes = {}
        if RANK_KEY in data:
            raw_data = data[RANK_KEY]
            if isinstance(raw_data, list):
                for rank_data in raw_data:
                    ranks.append(Rank.create(rank_data))
            else:
                ranks.append(Rank.create(raw_data))
        elif global_rank:
            ranks.append(Rank.create(global_rank))
        else:
            ranks.append(Rank.create_default())
        if ATTRIBUTE_KEY in data:
            raw_data = data[ATTRIBUTE_KEY]
            assert isinstance(raw_data, dict)
            for key in raw_data:
                assert type(raw_data[key]) in [unicode, list]
                attribute_value = [raw_data[key]] if type(raw_data[key]) is unicode else raw_data[key]
                attributes[key] = attribute_value
        location = data[LOCATION_KEY] if LOCATION_KEY in data else None
        if location and not os.path.exists(location):
            warning("directory \"%s\" does not exist" % location)
            return None
        return Image(pattern, group_name, ranks, attributes, option, size, location)

OPTION_KEY = "option"
SIZE_KEY = "size"


class SettingLoader(object):
    """load the image setting from json files"""

    def __init__(self, in_file):
        self.__json_loader = JsonLoader(in_file)
        self.group_name = os.path.basename(in_file[:in_file.rfind('.')])
        self.__option = None
        self.__size = None
        self.__global_rank = None
        self.images = {}
        self.load_setting()

    def load_setting(self):
        self.__option = self.__json_loader.get_root_obj(OPTION_KEY)
        self.__size = self.__json_loader.get_root_obj(SIZE_KEY)
        self.__global_rank = self.__json_loader.get_root_obj(RANK_KEY)
        root = self.__json_loader.get_root_obj("image")
        if not root:
            return
        assert isinstance(root, dict)
        for pattern in root:
            obj = Image.create(pattern, root[pattern], self.group_name, self.__option, self.__size, self.__global_rank)
            if obj:
                self.images[pattern] = obj

    def print(self):
        print("group name:", self.group_name)
        print("option:", self.__option)
        print("size:", self.__size)
        print("global rank:", self.__global_rank)
        for pattern in self.images:
            self.images[pattern].print()

if __name__ == '__main__':
    OBJ = SettingLoader("test_image.json")
    OBJ.print()
