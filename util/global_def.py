#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import logging


def is_mac_os():
    import platform
    system_name = platform.system()
    return "Darwin" in system_name


def get_delim_str():
    import platform
    system_name = platform.system()
    if "Darwin" in system_name:
        return "/"
    elif "Linux" in system_name:
        return "/"
    elif "Windows" in system_name:
        return "\\"
    return "/"  # default treats it an unix-like system


__DELIM = get_delim_str()


def get_delim():
    return __DELIM

NA = -1
__DATA_HOME = ""
__SLIDESHOW_FREQUENCY = 10  # the frequency in second to have slideshow
__PHRASE_APPEAR_RATIO = 100  # a fixed percentage ratio (0-100) to show phrase
__PHRASE_FONT_SIZE = 64#32  # phrase font size in pixel
__SEARCH_LATENCY = 3#1
__API_KEY = ''
__CX = ''
__FULLSCREEN_MODE2 = False
__NETWORK_ACCESSIBLE_PIVOT = 'http://google.com'


def set_accessible_pivot(accessible_pivot):
    global __NETWORK_ACCESSIBLE_PIVOT
    assert type(accessible_pivot) in [str, unicode]
    accessible_pivot = accessible_pivot.strip('\'').strip('"')
    http_prefix = "http://"
    if -1 == accessible_pivot.find(http_prefix):
        accessible_pivot = http_prefix + accessible_pivot
    __NETWORK_ACCESSIBLE_PIVOT = accessible_pivot


def get_accessible_pivot():
    return __NETWORK_ACCESSIBLE_PIVOT


def set_fullscreen_mode2(fullscreen_mode2):
    global __FULLSCREEN_MODE2
    __FULLSCREEN_MODE2 = fullscreen_mode2


def get_fullscreen_mode2():
    return __FULLSCREEN_MODE2


def set_api_key(api_key):
    global __API_KEY
    __API_KEY = api_key


def set_cx(cx):
    global __CX
    __CX = cx


def get_api_key():
    return __API_KEY if "" != __API_KEY else None


def get_cx():
    return __CX if "" != __CX else None


def set_search_latency(latency):
    assert latency >= 1
    global __SEARCH_LATENCY
    __SEARCH_LATENCY = latency


def get_search_latency():
    return __SEARCH_LATENCY


def get_slideshow_frequency():
    return __SLIDESHOW_FREQUENCY


def set_slideshow_frequency(slideshow_frequency):
    assert slideshow_frequency > 0
    global __SLIDESHOW_FREQUENCY
    __SLIDESHOW_FREQUENCY = slideshow_frequency


def set_phrase_appear_ratio(ratio):
    assert 0 <= ratio <= 100
    global __PHRASE_APPEAR_RATIO
    __PHRASE_APPEAR_RATIO = ratio


def get_phrase_appear_ratio():
    return __PHRASE_APPEAR_RATIO


def set_phrase_font_size(font_size):
    assert font_size > 0
    global __PHRASE_FONT_SIZE
    __PHRASE_FONT_SIZE = font_size


def get_phrase_font_size():
    return int(__PHRASE_FONT_SIZE)


def set_data_home(home):
    assert type(home) in [str, unicode]
    global __DATA_HOME
    __DATA_HOME = home
    if len(__DATA_HOME) > 0 and __DATA_HOME[-1] != get_delim():
        __DATA_HOME += get_delim()


def get_data_home():
    return __DATA_HOME


def get_user_config_file():
    return __DATA_HOME + "config.ini"


def config_action():
    config_file = get_user_config_file()
    if config_file:
        from util.config import Config
        Config(config_file).set_general_setting()

# We intend to use module-based logger, for other referenced module, e.g., requests, adopts logging as well.
# Thus, if not use module-based one, in verbose(debug) mode, message from referenced module will show.
__LOGGER = logging.getLogger("iReminder")

# the following to remove the duplicated logging message
# learn from
# http://stackoverflow.com/questions/31403679/python-logging-module-duplicated-console-output-ipython-notebook-qtconsole
__LOGGER.propagate = False


def set_logging_values(level, in_format):
    global __LOGGER
    __LOGGER.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(in_format))
    __LOGGER.addHandler(ch)


def debug(msg):
    __LOGGER.debug(msg)


def info(msg):
    __LOGGER.info(msg)


def warning(msg):
    __LOGGER.warning(msg)


def error(msg):
    __LOGGER.error(msg)
