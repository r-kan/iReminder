#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os
from argparse import ArgumentParser
from logging import INFO, DEBUG
from gui.graph_view.multi_viewer import MultiGraphViewer
from util.global_def import set_logging_values, debug


class IReminder(object):

    def __init__(self):
        parser = ArgumentParser(description='iReminder --- The Image Reminder')
        # TODO: break the limit that positional argument need to be in a continuous sequence
        # e.g., the following will error "aa bb -p cc dd" (error on 'dd')
        parser.add_argument('images', nargs='+', help='image pattern or pattern file (.list, .json)')
        parser.add_argument("-p", "--phrase", dest="phrases", action='append', default=None,
                            help="phrase or phrase file (.list, .json)")
        parser.add_argument("-c", "--config", dest="config", default=None, help="configuration file")
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=DEBUG, help="verbose mode")
        args = parser.parse_args()
        set_logging_values(level=args.verbose if args.verbose else INFO, in_format='')
        if args.config:
            from util.config import Config
            Config(args.config).set_general_setting()
        self.__image_setting = IReminder.flatten_settings(args.images)
        self.__phrase_setting = IReminder.flatten_settings(args.phrases)
        self.print_myself(args.verbose)

    @staticmethod
    def flatten_settings(raw_settings):
        if not raw_settings:
            return None
        settings = []
        for raw_setting in raw_settings:
            _, ext = os.path.splitext(raw_setting)
            if ext in [".list", ".json"]:  # a pattern file
                import glob
                settings += glob.glob(raw_setting)
            else:  # a raw text pattern
                settings.append(raw_setting)
        return settings

    def print_myself(self, verbose):
        if not verbose:
            return
        if self.__image_setting:
            debug("image:")
            for setting in self.__image_setting:
                debug('\t%s' % setting)
        if self.__phrase_setting:
            debug("phrase:")
            for setting in self.__phrase_setting:
                debug('\t%s' % setting)

    def run(self):
        MultiGraphViewer(self.__image_setting, self.__phrase_setting).view()


if __name__ == '__main__':
    IReminder().run()
