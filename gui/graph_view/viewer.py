#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import Tkinter

from collections import deque
from PIL import Image, ImageTk
import random
import sys
from base.graph_fetch.fetcher import GraphFetcher, DELETE, DISCARD, INC_RANK, DEC_RANK
from base.graph_fetch.fetcher import ImageSlot  # to let pickle can recognize ImageSlot
from base.dir_handle.dir_handler import GraphDirHandler
from base.setting.utility import RankArbitrator as Arbitrator
from base.setting.image import Image as ImageObj
from util.color import get_random_color
from util.global_def import debug, info, error, is_mac_os
from util.global_def import NA, get_slideshow_frequency, get_phrase_appear_ratio, get_fullscreen_mode2

__BG__ = 'black'


def user_quit(*unused):
    sys.exit()


class GraphViewer(object):
    """'randomly' show the crawled picture"""
    IMAGE_HISTORY_SIZE = 10

    def __init__(self):
        self.__root = Tkinter.Tk()
        self.__root.configure(background=__BG__)
        self.__root.title("iReminder")
        w, h = self.__root.winfo_screenwidth(), self.__root.winfo_screenheight()
        self.__full_geom = "%dx%d+0+0" % (w, h)
        self.__root.geometry(self.__full_geom)
        self.__old_label_image = None
        self.__pending_jobs = []
        self.__tk_obj_ref = None  # need keep ref to prevent GC (garbage collection)
        self.__onscreen_help = False
        self.__onscreen_info = False
        self.__pause_slideshow = False
        self.__fullscreen_mode = True
        if get_fullscreen_mode2():
            self.__root.overrideredirect(self.__fullscreen_mode)  # do this b4 ...'-fullscreen'
        self.__root.attributes("-fullscreen", self.__fullscreen_mode)
        self.__root.bind("<Escape>", self.toggle_display_mode)
        self.__root.bind("<BackSpace>", self.delete_image)
        self.__root.bind("<Button>", lambda e: e.widget.quit())
        self.__root.bind("<Right>", lambda e: e.widget.quit())
        self.__root.bind("<Left>", self.show_previous_image)
        self.__root.bind("<h>", self.toggle_onscreen_help)
        self.__root.bind("<H>", self.toggle_onscreen_help)
        self.__root.bind("<i>", self.toggle_onscreen_info)
        self.__root.bind("<I>", self.toggle_onscreen_info)
        self.__root.bind("<p>", self.toggle_pause_slideshow)
        self.__root.bind("<P>", self.toggle_pause_slideshow)
        self.__root.bind("<q>", user_quit)
        self.__root.bind("<Q>", user_quit)
        self.__root.bind("<equal>", self.increment_rank)
        self.__root.bind("<minus>", self.decrement_rank)
        self.__cur_image_obj = None
        self.__cur_image_obj_list = []  # image_obj in list
        self.__cur_image_obj_dict = {}  # image_obj in dict (same content as above)
        self.__phrase_binding = {}  # key: pattern, value: list of PhraseGroup
        self.__cur_phrase_obj_dict = {}  # key: phrase group name, value: PhraseGroup
        self.__cur_graph_file = None
        self.__graph_history = deque(maxlen=GraphViewer.IMAGE_HISTORY_SIZE)
        self.__cur_digest = ""
        self.__arbitrator = None
        self.__canvas = Tkinter.Canvas(self.__root, bg=__BG__, bd=0, highlightthickness=0)
        self.__canvas.pack(expand=Tkinter.YES, fill=Tkinter.BOTH)
        self.__help = self.help_text()
        self.__info = self.info_text()
        self.__phrase_var = Tkinter.StringVar()
        self.__phrase = self.phrase_text()

    def get_full_geom(self):
        w, h = self.__root.winfo_screenwidth(), self.__root.winfo_screenheight()
        return "%dx%d+0+0" % (w, h)

    def toggle_display_mode(self, *unused):
        self.__fullscreen_mode = not self.__fullscreen_mode
        self.__root.attributes("-fullscreen", self.__fullscreen_mode)
        if get_fullscreen_mode2():
            self.__root.overrideredirect(self.__fullscreen_mode)
        self.set_graph_content(self.__cur_graph_file)

    def delete_image(self, *unused):
        if self.__cur_image_obj.location:
            return  # spec.: not support remove image that user 'specified'
        info("remove image %s" % self.__cur_graph_file)
        self.__graph_history.remove([self.__cur_image_obj, self.__cur_graph_file])
        GraphFetcher.handle_image(self.__cur_graph_file, DELETE)
        self.cancel_pending_jobs()
        self.timer_action(True)

    def show_previous_image(self, *unused):
        last_graph = self.__graph_history.pop()
        self.__graph_history.appendleft(last_graph)
        self.set_graph(*self.__graph_history.pop())
        self.cancel_pending_jobs()
        self.prepare_for_next_view(get_slideshow_frequency() * 1000)

    def increment_rank(self, *unused):
        info("increase rank %s" % self.__cur_graph_file)
        if self.__cur_image_obj.location:
            msg = GraphDirHandler.handle_image(self.__cur_image_obj.location, self.__cur_graph_file, INC_RANK)
        else:
            msg = GraphFetcher.handle_image(self.__cur_graph_file, INC_RANK)
        self.__cur_digest += "\n%s" % msg
        self.show_onscreen_info()

    def decrement_rank(self, *unused):
        info("decrease rank %s" % self.__cur_graph_file)
        if self.__cur_image_obj.location:
            msg = GraphDirHandler.handle_image(self.__cur_image_obj.location, self.__cur_graph_file, DEC_RANK)
        else:
            msg = GraphFetcher.handle_image(self.__cur_graph_file, DEC_RANK)
        self.__cur_digest += "\n%s" % msg
        self.show_onscreen_info()

    def toggle_onscreen_help(self, *unused):
        """display the on-screen help message"""
        self.__onscreen_help = not self.__onscreen_help
        self.show_onscreen_help()

    def toggle_onscreen_info(self, *unused):
        self.__onscreen_info = not self.__onscreen_info
        self.show_onscreen_info()

    def toggle_pause_slideshow(self, *unused):
        self.__pause_slideshow = not self.__pause_slideshow
        self.show_onscreen_info()  # for the 'PAUSED' msg shown on onscreen_info

    # TODO:
    # for the following show_onscreen_XXX, it may not be a very good way to re-create canvas text?
    # better to call some api make it top-most again?
    def show_onscreen_help(self):
        self.__canvas.delete(self.__help)
        if not self.__onscreen_help:
            return
        self.__help = self.help_text()

    def show_onscreen_info(self):
        self.__canvas.delete(self.__info)
        if not self.__onscreen_info:
            return
        self.__info = self.info_text()

    def show_onscreen_phrase(self):
        self.__canvas.delete(self.__phrase)
        if "" == self.__phrase_var.get():
            return
        self.__phrase = self.phrase_text()

    def prepare_for_next_view(self, wait_time, msg=None):
        if msg:
            debug("[view] %s" % msg)
        job = self.__root.after(int(wait_time), lambda: self.timer_action())
        self.__pending_jobs.append(job)

    def cancel_pending_jobs(self):
        for job in self.__pending_jobs:
            self.__root.after_cancel(job)
        self.__pending_jobs = []

    def select_pattern(self):
        if self.__arbitrator.is_active():
            choice_pattern = None
            while not choice_pattern:
                choice_pattern = self.__arbitrator.arbitrate()
                if not choice_pattern:
                    debug("[view] no available image now, will wait for ten minutes...")
                    self.__root.withdraw()
                    import time
                    time.sleep(600)
            self.__root.deiconify()
            return self.__cur_image_obj_dict[choice_pattern]
        image_obj_size = len(self.__cur_image_obj_list)
        return self.__cur_image_obj_list[random.randrange(0, image_obj_size)]

    def get_resolved_sentence(self, sentence, pattern, phrase_obj):
        while "var" in sentence:
            pre_key = "var("
            post_key = ")"
            begin_var_name_offset = sentence.find(pre_key)
            assert -1 != begin_var_name_offset
            pos_begin_var_name = begin_var_name_offset + len(pre_key)
            end_var_name_offset = sentence[pos_begin_var_name:].find(post_key)
            assert -1 != end_var_name_offset
            var_name = sentence[pos_begin_var_name:pos_begin_var_name + end_var_name_offset]
            if '`' == var_name[0]:
                assert "pattern" == var_name[1:]
                replace_to = pattern
            else:
                if var_name in self.__cur_image_obj_dict[pattern].attributes:
                    attribute_values = self.__cur_image_obj_dict[pattern].attributes[var_name]
                    rand_idx = random.randrange(0, len(attribute_values))
                    replace_to = attribute_values[rand_idx]
                else:
                    replace_to = phrase_obj.get_default_value(sentence, var_name)
            sentence = sentence.replace(pre_key + var_name + post_key, replace_to)
        return sentence

    def select_phrase(self, pattern):
        if pattern not in self.__phrase_binding or get_phrase_appear_ratio() < float(random.randrange(0, 101)):
            self.__phrase_var.set("")
            return
        phrase_arbitrator = Arbitrator()
        for phrase_obj in self.__phrase_binding[pattern]:
            phrase_arbitrator.add_rank(phrase_obj.name, phrase_obj.rank)
        phrase_arbitrator.finalize_rank()
        arbitrated_phase = phrase_arbitrator.arbitrate()
        if not arbitrated_phase:
            self.__phrase_var.set("")
            return
        chosen_phrase_obj = self.__cur_phrase_obj_dict[arbitrated_phase]
        import os
        base_file_name = os.path.basename(self.__cur_graph_file)
        group_name = self.__cur_image_obj_dict[pattern].group_name
        chosen_sentence = chosen_phrase_obj.select_sentence(pattern, group_name, base_file_name)
        if not chosen_sentence:
            self.__phrase_var.set("")
            return
        resolved_sentence = self.get_resolved_sentence(chosen_sentence, pattern, chosen_phrase_obj)
        self.__phrase_var.set(resolved_sentence)

    FAIL_COUNT_TO_EXIT = 100
    CURR_FAIL_COUNT = 0

    def timer_action(self, user_next_image=False):
        if not user_next_image and self.__pause_slideshow:
            self.prepare_for_next_view(get_slideshow_frequency() * 1000)
            return
        success = self.set_graph(self.select_pattern())
        if not success:
            self.prepare_for_next_view(1, "try fetch image again")
            if GraphViewer.CURR_FAIL_COUNT >= GraphViewer.FAIL_COUNT_TO_EXIT:
                error("[view] fail to fetch more images, program exits")
                sys.exit()
            GraphViewer.CURR_FAIL_COUNT += 1
            return
        GraphViewer.CURR_FAIL_COUNT = 0
        self.prepare_for_next_view(get_slideshow_frequency() * 1000)

    def get_adjusted_geom(self, width, height):
        """output: resize_width, resize_height, x_pos, y_pos"""
        self.__root.geometry(self.__full_geom)  # self.__root.geometry(self.get_full_geom())
        x_root = self.__root.winfo_rootx()
        y_root = self.__root.winfo_rooty()
        full_width = self.__root.winfo_screenwidth() - x_root
        full_height = self.__root.winfo_screenheight() - y_root
        full_ratio = float(full_width) / float(full_height)
        image_ratio = float(width) / float(height)
        is_width_based = image_ratio > full_ratio
        expand_ratio = float(full_width if is_width_based else full_height) / \
            float(width if is_width_based else height)
        resize_width = int(expand_ratio * width)
        resize_height = int(expand_ratio * height)
        x_pos = (full_width - resize_width) / 2
        y_pos = (full_height - resize_height) / 2
        return resize_width, resize_height, x_pos, y_pos

    @staticmethod
    def get_image(file_handle):
        # Note:
        #   1. need convert to 'RGB' for some (transparent) format image cannot be shown using PhotoImage
        #      don't know why, but those image actually can be shown by Image itself (usg Image.show)
        #   2. use file_handle instead of filename, for in Windows, Image.open() seems not close its
        #      handle upon IOError, and thus, induces an unexpected file lock
        return Image.open(file_handle).convert("RGB")

    def set_graph_content(self, graph_file, image=None):
        if image is None:
            try:
                image = GraphViewer.get_image(graph_file)
            except IOError as e:
                error("[view] %s" % str(e))
                assert False
        self.__root.geometry(self.__full_geom if self.__fullscreen_mode else
                             '%dx%d+0+0' % (image.size[0], image.size[1]))
        if self.__fullscreen_mode:
            resize_width, resize_height, x_pos, y_pos = self.get_adjusted_geom(image.size[0], image.size[1])
            try:
                resized = image.resize((resize_width, resize_height), Image.ANTIALIAS)
            except IOError as e:
                # 'incomplete downloaded image' may go here
                info("fail to convert image to fullscreen: %s" % str(e))
                GraphFetcher().handle_image(graph_file, DISCARD)
                return False
            image = resized
        self.__root.title(self.__cur_image_obj.group_name)
        tk_image_obj = ImageTk.PhotoImage(image)
        self.__tk_obj_ref = tk_image_obj
        self.__canvas.delete('all')
        self.__canvas.create_image(x_pos if self.__fullscreen_mode else 0, y_pos if self.__fullscreen_mode else 0,
                                   image=tk_image_obj, anchor=Tkinter.NW)
        self.show_onscreen_help()
        self.show_onscreen_info()
        self.show_onscreen_phrase()
        return True

    def set_graph(self, image_obj, graph_file=NA):
        self.__cur_image_obj = image_obj
        digest = None
        if NA == graph_file:
            graph_file, digest = GraphDirHandler(image_obj.location).get_graph() if image_obj.location else \
                                 GraphFetcher(size=image_obj.size, option=image_obj.option).fetch(image_obj.pattern)
        if NA == graph_file:
            return False
        debug("[view] %s" % graph_file)
        with open(graph_file, 'rb') as f:
            try:
                image = GraphViewer.get_image(f)
            except IOError as e:
                f.close()  # close f here for we are going to delete the file below
                # some image cannot be opened (maybe it's not image format?), err msg is 'cannot identify image file'
                info("fail to open image: %s" % str(e))
                GraphFetcher().handle_image(graph_file, DELETE)
                return False
            # we met "Decompressed Data Too Large" for ~/Inside Out/Image_124.jpg...
            except ValueError as e:
                info("fail to open image: %s" % str(e))
                return False
        self.__cur_graph_file = graph_file
        self.__graph_history.append([self.__cur_image_obj, self.__cur_graph_file])
        if digest:
            digest_str = digest + "\n"
        else:
            digest_str = "%s：%s\n" % ("path", graph_file)
        self.__cur_digest = digest_str + "size：%sx%s" % (image.size[0], image.size[1])
        self.select_phrase(image_obj.pattern)
        return self.set_graph_content(graph_file, image)

    def setup_image_stuff(self, image_obj_list):
        self.__cur_image_obj_list = image_obj_list
        self.__arbitrator = Arbitrator()
        self.__cur_image_obj_dict = {}
        for image_obj in self.__cur_image_obj_list:
            self.__cur_image_obj_dict[image_obj.pattern] = image_obj
            if not image_obj.ranks:
                continue
            self.__arbitrator.add_rank(image_obj.pattern, image_obj.ranks[0])
        self.__arbitrator.finalize_rank()

    def setup_phrase_stuff(self, image_obj_list, phrase_obj_list):
        for image_obj in image_obj_list:
            pattern = image_obj.pattern
            for phrase_obj in phrase_obj_list:
                if pattern in phrase_obj.targets or image_obj.group_name in phrase_obj.targets or \
                      not phrase_obj.targets:
                    if pattern not in self.__phrase_binding:
                        self.__phrase_binding[pattern] = []
                    self.__phrase_binding[pattern].append(phrase_obj)
        for phrase_obj in phrase_obj_list:
            self.__cur_phrase_obj_dict[phrase_obj.name] = phrase_obj

    @staticmethod
    def set_front():
        if is_mac_os():
            import os
            # TODO: "21:62: execution error: Finder got an error: Can’t set process "Python" to true. (-10006)"
            # above error might occasionally happens when multiple instances initializing...
            # currently it won't induce major problem and thus we somehow ignore it by letting the err msg fade away
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' >& /dev/null''')

    def view(self, image_obj_list, phrase_obj_list):
        if not phrase_obj_list:
            # the WTF 'mutable default argument' property makes us not have [] firstly
            phrase_obj_list = []
        if not image_obj_list:
            info("not any image is specified, program exits")
            sys.exit()
        self.setup_image_stuff(image_obj_list)
        self.setup_phrase_stuff(image_obj_list, phrase_obj_list)
        GraphViewer.set_front()
        while True:
            self.timer_action(True)
            self.__root.mainloop()
            self.cancel_pending_jobs()

    def help_text(self):
        return self.__canvas.create_text(0, 0, anchor=Tkinter.NW, font=("system", -15),
                                         text=GraphViewer.help_str(), fill="red", activefill=get_random_color())

    def info_text(self):
        text = self.__cur_digest
        if self.__pause_slideshow:
            text += "\n[PAUSED]"
        return self.__canvas.create_text(0, 20, anchor=Tkinter.NW, font=("system", -15),
                                         text=text, fill="blue", activefill=get_random_color())

    def phrase_text(self):
        smallest_y = 0.1 * self.__root.winfo_screenheight()
        largest_y = 0.9 * self.__root.winfo_screenheight()
        smallest_x = 10
        # Not so good to have fixed 0.25 value, maybe we can enhance it later
        largest_x = 0.25 * self.__root.winfo_screenwidth()
        from util.global_def import get_phrase_font_size
        return self.__canvas.create_text(random.randrange(smallest_x, largest_x),
                                         random.randrange(smallest_y, largest_y),
                                         anchor=Tkinter.SW, font=("system", -1 * get_phrase_font_size()),
                                         text=self.__phrase_var.get(),
                                         fill=get_random_color(),
                                         activefill=get_random_color())

    @staticmethod
    def help_str():
        def is_osx():
            import platform
            system_name = platform.system()
            return "Darwin" in system_name
        delete_button = "delete" if is_osx() else "backspace"
        return "esc:switch fullscreen|" + delete_button + ":remove image|h:help|i:info|->:next|<-:prev|p:pause|q:quit"


if __name__ == '__main__':
    from argparse import ArgumentParser
    arg_parser = ArgumentParser(description='iReminder --- pure viewer')
    arg_parser.add_argument('patterns', nargs='+')
    args = arg_parser.parse_args()
    from util.global_def import config_action
    config_action()
    GraphViewer().view([ImageObj(pattern) for pattern in args.patterns], None)
