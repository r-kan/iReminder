#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from util.global_def import set_phrase_appear_ratio, get_phrase_appear_ratio, \
    set_slideshow_frequency, get_slideshow_frequency, \
    set_search_latency, get_search_latency, \
    set_api_key, set_cx, get_api_key, get_cx, \
    set_data_home, get_data_home, \
    set_phrase_font_size, get_phrase_font_size, \
    set_fullscreen_mode2, get_fullscreen_mode2, \
    set_accessible_pivot, get_accessible_pivot


class Config(object):

    def __init__(self, config_file):
        import os
        if not os.path.exists(config_file):
            print("config file \"%s\" does not exist, program exits..." % config_file)
            import sys
            sys.exit()
        from ConfigParser import ConfigParser
        self.__config = ConfigParser()
        self.__config.read(config_file)

    def set_general_setting(self):
        data_home = get_data_home() if not self.__config.has_option("global", "data_location") else \
            self.__config.get("global", "data_location")
        accessible_pivot = get_accessible_pivot() if not self.__config.has_option("global", "network_accessible_pivot") else \
            self.__config.get("global", "network_accessible_pivot")
        slideshow_frequency = get_slideshow_frequency() if not self.__config.has_option("image", "slideshow_frequency") else \
            float(self.__config.get("image", "slideshow_frequency"))
        fullscreen_mode2 = get_fullscreen_mode2() if not self.__config.has_option("image", "fullscreen_mode2") else \
            "True" == self.__config.get("image", "fullscreen_mode2")
        phrase_appear_ratio = get_phrase_appear_ratio() if not self.__config.has_option("phrase", "ratio") else \
            float(self.__config.get("phrase", "ratio"))
        phrase_font_size = get_phrase_font_size() if not self.__config.has_option("phrase", "font_size") else \
            float(self.__config.get("phrase", "font_size"))
        api_key = get_api_key() if not self.__config.has_option("search", "api_key") else \
            self.__config.get("search", "api_key")
        cx = get_cx() if not self.__config.has_option("search", "cx") else \
            self.__config.get("search", "cx")
        search_latency = get_search_latency() if not self.__config.has_option("search", "search_latency") else \
            float(self.__config.get("search", "search_latency"))
        set_data_home(data_home)
        set_accessible_pivot(accessible_pivot)
        set_slideshow_frequency(slideshow_frequency)
        set_fullscreen_mode2(fullscreen_mode2)
        set_phrase_appear_ratio(phrase_appear_ratio)
        set_phrase_font_size(phrase_font_size)
        set_search_latency(search_latency)
        set_api_key(api_key)
        set_cx(cx)
        print("=======  iReminder setting  =============")  # currently, we only show selected entries
        print("data home:       ", data_home)
        print("slideshow:       ", slideshow_frequency)
        print("phrase ratio:    ", phrase_appear_ratio)
        print("search latency:  ", search_latency)
        print("========================================")

    def get_setting(self, section, option):
        if self.__config.has_option(section, option):
            return self.__config.get(section, option)
        else:
            return None
