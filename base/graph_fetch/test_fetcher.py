#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from base.graph_fetch.fetcher import GraphFetcher
from util.serialize import load


class TestFetcher(object):
    """testing related function for GraphFetcher"""

    @staticmethod
    def print_pattern(pattern):
        print("image：", pattern)
        # print(GraphFetcher.get_cache_file(pattern))
        [has_cache, cached_objs] = load(GraphFetcher.get_cache_file(pattern))
        assert has_cache
        for url, i in zip(cached_objs, range(len(cached_objs))):
            image_slot = cached_objs[url]
            # print("order：", i)
            print("url：", url)
            print("timestamp：", image_slot.timestamp)
            print("no.：", image_slot.encoding)
            print("rank：", image_slot.rank)

    @staticmethod
    def traverse():
        for pattern in GraphFetcher.get_cache_patterns():
            TestFetcher.print_pattern(pattern)
            continue


if __name__ == '__main__':
    from util.global_def import config_action
    config_action()
    TestFetcher.traverse()
