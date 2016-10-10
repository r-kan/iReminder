#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from PIL import Image, ImageTk
import Tkinter
from util.color import get_random_color
import random


# TODO: the following image cannot be shown even in Image.show()
graph_file = "/Users/rodion/dev/reminder/base/graph_fetch/picture/インサイドヘッド/image_71.jpg"
# this one has strange result
graph_file2 = "/Users/rodion/reminder/picture/believe/image_66.jpg"
image = Image.open(graph_file2)
print(image.width, image.height)
print(image.format, image.mode)
# image.show()

root = Tkinter.Tk()
tmp = None
try:
    image = Image.open(graph_file2)  # .convert("RGB")
    tmp = image
except IOError as e:
    # some image cannot be opened (maybe it's not image format?), err msg is 'cannot identify image file'
    print("cannot open image", str(e))
root.geometry('%dx%d+0+0' % (image.size[0], image.size[1]))
tk_image_obj = ImageTk.PhotoImage(tmp)
label_image = Tkinter.Label(root, image=tk_image_obj)
label_image.place(x=0, y=0, width=image.size[0], height=image.size[1])
label_image.pack()

phrase_var = Tkinter.StringVar()
phrase_var.set("some test phrase")
phrase = Tkinter.Label(root, textvariable=phrase_var, bg='black', fg=get_random_color(),
                       justify=Tkinter.LEFT, anchor=Tkinter.SW, font=("system", 32))
smallest_y = 120
largest_y = 300
smallest_x = 10
largest_x = 300

phrase.place(x=random.randrange(smallest_x, largest_x),
             y=random.randrange(smallest_y, largest_y))

root.mainloop()
