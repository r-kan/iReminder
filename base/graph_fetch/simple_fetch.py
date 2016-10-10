#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os
import urllib2

url = "http://xxx.com/yyy.jpg"
abs_graph_file = "foo.jpg"
try:
    f = open(abs_graph_file, 'wb')
    print("fetch image：", url)
    f.write(urllib2.urlopen(url, timeout=3).read())
    f.close()
    # image.retrieve(url, abs_graph_file)
    assert os.path.exists(abs_graph_file)
    print("fetch succeed！")
except IOError as e:
    print("cannot store image：", url)
