#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from util.global_def import set_attach_rate, get_attach_rate, \
    set_slideshow_rate, get_slideshow_rate, \
    set_latency, get_latency, \
    set_search_size, get_search_size, \
    set_img_size, get_img_size, \
    set_api_key, set_cx, get_api_key, get_cx, \
    set_data_home, get_data_home, \
    set_font_size, get_font_size, \
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
        # global
        data_home = get_data_home() if not self.__config.has_option("global", "data_location") else \
            self.__config.get("global", "data_location")
        accessible_pivot = get_accessible_pivot() if not self.__config.has_option("global", "network_accessible_pivot") else \
            self.__config.get("global", "network_accessible_pivot")
        set_data_home(data_home)
        set_accessible_pivot(accessible_pivot)
        # search
        api_key = get_api_key() if not self.__config.has_option("search", "api_key") else \
            self.__config.get("search", "api_key")
        cx = get_cx() if not self.__config.has_option("search", "cx") else \
            self.__config.get("search", "cx")
        latency = get_latency() if not self.__config.has_option("search", "latency") else \
            float(self.__config.get("search", "latency"))
        search_size = get_search_size() if not self.__config.has_option("search", "search_size") else \
            int(self.__config.get("search", "search_size"))
        if self.__config.has_option("search", "img_size"):
            img_size = list(set(self.__config.get("search", "img_size").split('|')))  # 'set' to uniquify
        else:
            img_size = get_img_size()
        set_api_key(api_key)
        set_cx(cx)
        set_latency(latency)
        set_search_size(search_size)
        set_img_size(img_size)
        # image
        slideshow_rate = get_slideshow_rate() if not self.__config.has_option("image", "slideshow_rate") else \
            float(self.__config.get("image", "slideshow_rate"))
        fullscreen_mode2 = get_fullscreen_mode2() if not self.__config.has_option("image", "fullscreen_mode2") else \
            "True" == self.__config.get("image", "fullscreen_mode2")
        set_slideshow_rate(slideshow_rate)
        set_fullscreen_mode2(fullscreen_mode2)
        # phrase
        attach_rate = get_attach_rate() if not self.__config.has_option("phrase", "attach_rate") else \
            float(self.__config.get("phrase", "attach_rate"))
        font_size = get_font_size() if not self.__config.has_option("phrase", "font_size") else \
            float(self.__config.get("phrase", "font_size"))
        set_attach_rate(attach_rate)
        set_font_size(font_size)
        print("=======  iReminder setting  =============")  # currently, we only show selected entries
        print("data home:      ", data_home)
        print("slideshow rate: ", slideshow_rate)
        print("attach rate:    ", attach_rate)
        print("latency:        ", latency)
        print("search size:    ", search_size)
        print("========================================")

    def get_setting(self, section, option):
        if self.__config.has_option(section, option):
            return self.__config.get(section, option)
        else:
            return None
