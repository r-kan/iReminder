#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from base.setting.image import Image as ImageObj, SettingLoader as ImageSettingLoader
from base.setting.phrase import SettingLoader as PhraseSettingLoader, GLOBAL_KEY
from base.dir_handle.dir_handler import Status  # to let pickle can recognize Status
import os


def get_list_setting(list_file, is_image=False, is_phrase=False):
    assert is_image ^ is_phrase
    patterns = [pattern.strip() for pattern in open(list_file, 'r').readlines()]
    return patterns if is_phrase else [ImageObj(pattern) for pattern in patterns]


def get_json_setting(json_file, is_image=False, is_phrase=False):
    assert is_image ^ is_phrase
    entries = ImageSettingLoader(json_file).images if is_image else PhraseSettingLoader(in_file=json_file).phrases
    return [entries[key] for key in entries]


def get_objects(settings, is_image=False, is_phrase=False):
    if not settings:
        return
    assert is_image ^ is_phrase  # one and only one is True
    objects = []
    global_sentences = []
    for setting in settings:
        _, ext = os.path.splitext(setting)
        if ".list" == ext:
            if is_image:
                objects += get_list_setting(setting, is_image, is_phrase)
            else:
                global_sentences += get_list_setting(setting, is_image, is_phrase)
        elif ".json" == ext:
            objects += get_json_setting(setting, is_image, is_phrase)
        else:
            if is_image:
                objects.append(ImageObj(setting))
            else:
                global_sentences.append(setting)
    if is_phrase and global_sentences:
        objects.append(PhraseSettingLoader(in_sentences=global_sentences).phrases[GLOBAL_KEY])
    return objects


class MultiGraphViewer(object):

    def __init__(self, image_settings, phrase_settings):
        self.__images = get_objects(image_settings, is_image=True)
        self.__phrases = get_objects(phrase_settings, is_phrase=True)

    def view(self):
        from viewer import GraphViewer
        GraphViewer().view(self.__images, self.__phrases)
