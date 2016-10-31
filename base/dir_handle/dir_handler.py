#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os
import time
from base.graph_fetch.fetcher import INC_RANK, DEC_RANK
from util.global_def import info
from util.global_def import NA, get_delim
from util.select import get_weighted_random_dict_key
from util.serialize import save, load


class Status(object):

    def __init__(self):
        self.rank = 1


class GraphDirHandler(object):
    """handle the existed image files within given directory"""
    RECOGNIZED_IMAGE_EXT = ["jpg", "JPG", "jpeg", "JPEG"]
    CACHE_FILE = "iReminder.pickle"

    def __init__(self, location):
        self.__location = location
        assert os.path.exists(self.__location)
        self.__status_cache = self.__load_or_create_status()
        self.__valid = True

    @staticmethod
    def handle_image(location, graph_file, action):
        assert action in [INC_RANK, DEC_RANK]
        handler = GraphDirHandler(location)
        assert handler.__valid
        base_file = graph_file.replace(location + get_delim(), "")
        for image in handler.__status_cache:
            if image == base_file:
                has_change = True
                status = handler.__status_cache[image]
                if INC_RANK == action:
                    status.rank += 1
                    msg = "change rank to " + str(status.rank)
                else:
                    if 1 == status.rank:
                        msg = "cannot lower down rank as it is already the lowest!"
                        has_change = False
                    else:
                        status.rank -= 1
                        msg = "change rank to " + str(status.rank)
                if has_change:
                    handler.__status_cache[image] = status
                    cache_file = location + get_delim() + GraphDirHandler.CACHE_FILE
                    # TODO: it shows that the timestamp not change...
                    timestamp = time.ctime(os.path.getmtime(location))
                    save(cache_file, [timestamp, handler.__status_cache])
                return msg
        assert False

    def dir_changed(self, timestamp):
        # TODO: not a very good way
        return time.ctime(os.path.getmtime(self.__location)) != timestamp

    def __load_or_create_status(self):
        status_cache = {}  # key: image_file, value: status
        cache_file = self.__location + get_delim() + GraphDirHandler.CACHE_FILE
        cache_existed = os.path.exists(cache_file)
        if cache_existed:
            success, cache_data = load(cache_file)
            assert success
            [timestamp, status_cache] = cache_data
            if not self.dir_changed(timestamp):
                return status_cache
            else:
                info("directory %s has changed, update cache file" % self.__location)
        else:
            info("create a new cache file for directory: %s" % self.__location)
        image_files = []
        for root, _, files in os.walk(self.__location):
            assert len(root) >= 1
            if root[-1] != get_delim():
                root += get_delim()
            for base_file in files:
                basename, ext = os.path.splitext(base_file)
                if ext.replace(".", "") in GraphDirHandler.RECOGNIZED_IMAGE_EXT:
                    image_files.append((root + base_file).replace(self.__location + get_delim(), ""))
        if not image_files:
            if cache_existed:
                os.remove(cache_file)
            self.__valid = False
            return None
        existed_image = {}
        for image in image_files:
            existed_image[image] = 1  # 1 is just a dummy value
            if image not in status_cache:
                status_cache[image] = Status()
        to_be_deleted = []
        for image in status_cache:  # this check works when some image is deleted
            if image not in existed_image:
                to_be_deleted.append(image)
        for image in to_be_deleted:
            status_cache.pop(image)
        # TODO: this makes an 'always' has-changed 2nd time image
        timestamp = time.ctime(os.path.getmtime(self.__location))
        save(cache_file, [timestamp, status_cache])
        return status_cache

    def get_graph_digest(self, graph_file):
        if NA is graph_file:
            return "NA"
        full_graph_file = self.__location + get_delim() + graph_file
        timestamp = time.ctime(os.path.getmtime(full_graph_file))
        return "location：%s\ntimestamp：%s\nrank：%s" % (
            full_graph_file,
            timestamp,
            self.__status_cache[graph_file].rank)

    def get_graph(self):
        if not self.__valid:
            return NA, NA
        graph_file = get_weighted_random_dict_key(self.__status_cache)
        full_graph_file = self.__location + get_delim() + graph_file
        return full_graph_file, self.get_graph_digest(graph_file)


if __name__ == '__main__':
    OBJ = GraphDirHandler("/Users/rodion/Pictures/book")
    graph, digest = OBJ.get_graph()
    print(graph)
    print(digest)
