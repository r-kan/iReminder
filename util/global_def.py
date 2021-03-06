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
__SLIDESHOW_RATE = 10  # the frequency in second to have slideshow
__ATTACH_RATE = 100  # a fixed percentage ratio (0-100) to show phrase
__FONT_SIZE = 32  # phrase font size in pixel
__LATENCY = 3
__SEARCH_SIZE = 10

__VALID_IMG_SIZE = ["icon", "small", "medium", "large", "xlarge", "xxlarge", "huge"]
__IMG_SIZE = ["xlarge"]
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


__BUILTIN_API_KEY = "AIzaSyDcYhAlzkSqurlhVGqL9T0N2y7pfC_PBOk"
__BUILTIN_CX = "008963192842962532112:qahbrgj5bu4"


def set_api_key(api_key):
    global __API_KEY
    if api_key == __BUILTIN_API_KEY:
        warning("built-in 'api_key' can exhaust search quota indefinitely, suggest to create your own 'api_key'")
    __API_KEY = api_key


def set_cx(cx):
    global __CX
    if cx == __BUILTIN_CX:
        warning("built-in 'cx' is for a runnable example, suggest to create your own 'cx'")
    __CX = cx


def get_api_key():
    return __API_KEY if "" != __API_KEY else None


def get_cx():
    return __CX if "" != __CX else None


def set_latency(latency):
    assert latency >= 1
    global __LATENCY
    __LATENCY = latency


def get_latency():
    return __LATENCY


def set_search_size(search_size):
    assert search_size >= 1
    if search_size <= 10:  # one GCS search shall give 10 results, then no reason to have unit_size less than 10
        search_size = 10
    global __SEARCH_SIZE
    __SEARCH_SIZE = search_size


def get_search_size():
    return __SEARCH_SIZE


def set_img_size(img_size):
    assert type(img_size) is list
    recognized = []
    for size_item in img_size:
        assert type(size_item) in [str, unicode]
        if size_item not in __VALID_IMG_SIZE:
            warning("[config] '%s' is not a value image size specifier" % size_item)
        else:
            recognized.append(str(size_item))
    global __IMG_SIZE
    __IMG_SIZE = recognized


def get_img_size():
    return __IMG_SIZE


def get_slideshow_rate():
    return __SLIDESHOW_RATE


def set_slideshow_rate(slideshow_rate):
    assert slideshow_rate > 0
    global __SLIDESHOW_RATE
    __SLIDESHOW_RATE = slideshow_rate


def set_attach_rate(attach_rate):
    assert 0 <= attach_rate <= 100
    global __ATTACH_RATE
    __ATTACH_RATE = attach_rate


def get_attach_rate():
    return __ATTACH_RATE


def set_font_size(font_size):
    assert font_size > 0
    global __FONT_SIZE
    __FONT_SIZE = font_size


def get_font_size():
    return int(__FONT_SIZE)


def set_data_home(home):
    assert type(home) in [str, unicode]
    global __DATA_HOME
    __DATA_HOME = home
    if len(__DATA_HOME) > 0 and __DATA_HOME[-1] != get_delim():
        __DATA_HOME += get_delim()


def get_data_home():
    return __DATA_HOME


def get_user_config_file():
    return __DATA_HOME + "setting.ini"


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
