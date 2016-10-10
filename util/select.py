#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import random


def get_random_dict_key(objs):
    obj_size = len(objs)
    assert obj_size >= 1
    rand_idx = random.randrange(0, obj_size)
    for key, i in zip(objs, range(obj_size)):
        if i != rand_idx:
            continue
        return key
    assert False


class RankHolder(object):

    def __init__(self, rank):
        self.rank = rank


def get_weighted_random_dict_key(dice, bypass=None):
    """dice: dict with entry with 'rank' field, bypass: input [dict value], output [if this entry is skipped]"""
    key_pool = {}  # key: integer index, value: key
    ranked_choice_list = []
    obj_size = len(dice)
    for key, i in zip(dice, range(obj_size)):
        entry = dice[key]
        if bypass and bypass(entry):
            # print("bypass:", entry.encoding, key)
            continue
        key_pool[i] = key
        ranked_choice_list += [i] * entry.rank
    rand_idx = random.choice(ranked_choice_list)
    return key_pool[rand_idx]
