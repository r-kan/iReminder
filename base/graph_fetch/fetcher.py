#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import collections
import glob
import httplib
import os
import random
import ssl
import urllib2
from datetime import datetime
from base.crawler.graph_search import Crawler
from util.global_def import debug, info, error
from util.global_def import NA, get_data_home, get_delim, get_img_size
from util.network import reachable as network_reachable
from util.select import get_random_dict_key, get_weighted_random_dict_key
from util.serialize import save, load

ImageSlot = collections.namedtuple('ImageSlot', ('timestamp', 'encoding', 'rank'))

DELETE = 1  # remove image, and skip fetching from corresponding url again
DISCARD = 2  # remove image, and will re-fetching from corresponding url
INC_RANK = 3
DEC_RANK = 4


def pic_home():
    return get_data_home() + "picture" + get_delim()


def pickle_home():
    return get_data_home() + "pickle" + get_delim()


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        import errno
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise


class GraphFetcher(object):
    """fetch graph by url from crawler"""

    def __init__(self, setting=None, size=None, option=None):
        self.__setting = setting
        self.__size = size if size else get_img_size()
        self.__option = option
        self.__network_reachable = network_reachable()
        self.__has_write = False

    @staticmethod
    def get_cache_file(pattern):
        return pickle_home() + str(pattern) + ".pickle"

    @staticmethod
    def get_cache_patterns():
        cache_file_list = glob.glob(pickle_home() + "*.pickle")
        pattern_list = []
        for cache_file in cache_file_list:
            pos_begin = cache_file.find(pickle_home())
            assert 0 == pos_begin
            pos_end = cache_file.find(".pickle")
            assert -1 != pos_end
            pattern_list.append(cache_file[len(pickle_home()):pos_end])
        return iter(pattern_list)

    def fetch(self, pattern):
        self.__has_write = False
        new_objs, old_objs = self.get_updated_url(pattern)
        debug("[fetch] total data count: %s" % str(len(new_objs) + len(old_objs)))
        url = self.choose_url(new_objs, old_objs)
        if NA == url:
            return NA, NA
        image_objs = old_objs
        image_objs.update(new_objs)
        image_slot = image_objs[url]
        graph_file, new_encoding = self.get_graph_file(pattern, url, image_slot.encoding)
        new_slot = ImageSlot(image_slot.timestamp, new_encoding, image_slot.rank)
        image_objs[url] = new_slot
        if self.__has_write:
            save(GraphFetcher.get_cache_file(pattern), image_objs)
        return graph_file, GraphFetcher.get_graph_digest(graph_file, image_objs[url])

    @staticmethod
    def get_graph_digest(graph_file, url_obj):
        if NA is graph_file:
            return "NA"
        relative_pos = graph_file.find(pic_home())
        assert 0 == relative_pos
        relative_graph_file = graph_file[len(pic_home()):]
        return "%s：%s\n%s：%s\n%s：%s" % (
            "location", relative_graph_file,
            "timestamp", url_obj.timestamp.strftime("%B %d, %Y"),
            "rank", url_obj.rank)

    @staticmethod
    def choose_url(new_objs, old_objs):
        # ... support setting...
        new_size = len(new_objs)
        old_size = len(old_objs)
        if new_size > 0 and new_size + old_size <= new_size * 2:
            new_objs.update(old_objs)
            return get_random_dict_key(new_objs)
        if not old_size > 0:
            return NA
        # now we will throw a dice with 50%/50% prob. choosing new or old obj
        is_choose_new = new_size > 0 and 1 == random.randrange(0, 2)
        if is_choose_new:
            return get_random_dict_key(new_objs)
        else:
            return get_weighted_random_dict_key(old_objs, bypass=lambda image_slot: NA == image_slot.encoding)

    def get_updated_url(self, pattern):
        has_cache, cached_objs = load(GraphFetcher.get_cache_file(pattern))
        recent_url, is_new_result = Crawler().crawl(pattern, self.__size, self.__option)
        self.__has_write = is_new_result
        new_objs = {}
        if recent_url:
            for url in recent_url:
                if has_cache and url in cached_objs:
                    image_slot = cached_objs[url]
                    if is_new_result:
                        # update to current date
                        updated_slot = ImageSlot(datetime.today(), image_slot.encoding, image_slot.rank)
                        new_objs[url] = updated_slot
                    else:
                        new_objs[url] = image_slot
                else:
                    default_rank = 1
                    new_slot = ImageSlot(timestamp=datetime.today(), encoding=None, rank=default_rank)
                    new_objs[url] = new_slot  # a new entry
        if not has_cache:
            return new_objs, {}
        old_objs = {}
        for url in cached_objs:
            if not recent_url or url not in recent_url:
                old_objs[url] = cached_objs[url]
        return new_objs, old_objs

    def get_graph_file(self, pattern, url, cached_encoding):
        """output: graph_file, encoding"""
        if NA == cached_encoding:  # mean this url is not retrievable
            return NA, NA
        file_encoding = cached_encoding
        if not file_encoding:
            file_encoding = GraphFetcher.get_file_encoding(pattern)
        graph_dir = GraphFetcher.get_graph_dir(pattern)
        if not os.path.exists(graph_dir):
            try:
                mkdir_p(graph_dir)
            except OSError as e:
                error("[fetch] cannot create program directory, program exits:")
                error(str(e))
                import sys
                sys.exit()
        abs_graph_file = graph_dir + "image_" + file_encoding + ".jpg"
        if os.path.exists(abs_graph_file):
            return abs_graph_file, file_encoding
        if not self.__network_reachable:
            info("give up fetching image (due to no network connection):")
            return NA, None
        self.__has_write = True
        try:
            info("fetch image: %s" % url)
            try:
                web_content = urllib2.urlopen(url, timeout=10)
            except httplib.BadStatusLine:
                info("give up fetching image (due to no network connection): %s" % url)
                return NA, NA
            fd = open(abs_graph_file, 'wb')
            fd.write(web_content.read())
            fd.close()
            assert os.path.exists(abs_graph_file)
            if os.stat(abs_graph_file).st_size <= 10240:
                info("give up acquired image with size: %s Bytes" % os.stat(abs_graph_file).st_size)
                info("remove image: %s" % abs_graph_file)
                os.remove(abs_graph_file)
                return NA, NA
            info("fetch succeeded")
            return abs_graph_file, file_encoding
        except (IOError, httplib.IncompleteRead, ssl.CertificateError) as e:
            info("failed url: %s" % url)
            info("error: %s" % str(e))
            if os.path.exists(abs_graph_file):
                fd.close()
                os.remove(abs_graph_file)
            return NA, NA

    # noinspection PyShadowingNames
    @staticmethod
    def handle_image(graph_file, action):
        assert action in [DELETE, DISCARD, INC_RANK, DEC_RANK]
        key_str = get_delim() + "image_"
        end_pos = graph_file.find(key_str)
        assert -1 != end_pos
        begin_pos = graph_file[:end_pos].rfind(get_delim())
        assert -1 != begin_pos
        pattern = graph_file[begin_pos + 1:end_pos]
        has_cache, cached_objs = load(GraphFetcher.get_cache_file(pattern))
        assert has_cache
        file_encoding = graph_file[graph_file.find(key_str) + len(key_str):graph_file.find(".jpg")]
        for url in cached_objs:
            image_slot = cached_objs[url]
            if image_slot.encoding == file_encoding:
                new_encoding = NA if DELETE == action else \
                    None if DISCARD == action else \
                    image_slot.encoding  # no change
                new_rank = image_slot.rank + 1 if INC_RANK == action else \
                    image_slot.rank - 1 if DEC_RANK == action and image_slot.rank is not 1 else \
                    image_slot.rank  # no change
                updated_slot = ImageSlot(timestamp=image_slot.timestamp,
                                         encoding=new_encoding,
                                         rank=new_rank)
                cached_objs[url] = updated_slot
                save(GraphFetcher.get_cache_file(pattern), cached_objs)
                if action in [DELETE, DISCARD]:
                    os.remove(graph_file)
                msg = "" if action in [DELETE, DISCARD] else \
                    "change rank to " + str(new_rank) + "！" if new_rank is not image_slot.rank else \
                    "cannot lower down rank as it is already the lowest!" if image_slot.rank is 1 else \
                    None
                assert msg is not None
                return msg
        assert False

    @staticmethod
    def get_graph_dir(pattern):
        return pic_home() + str(pattern) + get_delim()

    @staticmethod
    def get_file_encoding(pattern):
        # TODO: add a file to keep last largest number to avoid possible long glob time...
        file_list = glob.glob(GraphFetcher.get_graph_dir(pattern) + "image_*.jpg")
        largest_idx = 0
        # noinspection PyShadowingNames
        for graph_file in file_list:
            begin_pos = graph_file.find("image_")
            end_pos = graph_file.find(".jpg")
            assert -1 != begin_pos and -1 != end_pos
            begin_pos += len("image_")
            iter_idx = int(graph_file[begin_pos:end_pos])
            assert iter_idx > 0
            largest_idx = iter_idx if iter_idx > largest_idx else largest_idx
        largest_idx += 1
        return str(largest_idx)


if __name__ == '__main__':
    from util.global_def import config_action
    config_action()
    # name '_' before the 'obj' to let python not free imported module before __del__ is called
    # (or we will have 'NoneType' object has no attribute 'dump' for cPickle.dump)
    _obj = GraphFetcher()
    graph_file, digest = _obj.fetch("Inside Out")
    if NA == graph_file:
        print("fetch image fail")
    else:
        print(graph_file)
