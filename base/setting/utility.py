#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from util.select import RankHolder, get_weighted_random_dict_key
from util.global_def import warning

PERCENTAGE = 1
WEIGHT = 2


class RankArbitrator(object):

    def __init__(self):
        self.__general_ranks = {}  # key: pattern, value: list of Rank => un-timed rank
        self.__timed_ranks = {}  # ranks with period constraint (separate this field for faster 'time-filtering' phase)
        self.__general_percentage_count = 0
        self.__general_percentage_holder = {}  # key: pattern, value: RankHolder
        self.__general_weight_holder = {}

    def is_active(self):
        return self.__general_ranks or self.__timed_ranks

    def add_rank(self, pattern, rank):
        target_rank = self.__general_ranks if rank.period.empty else self.__timed_ranks
        if pattern not in target_rank:
            target_rank[pattern] = []
        rank_list = target_rank[pattern]
        rank_list.append(rank)

    def finalize_rank(self):
        """prepare general holders for faster arbitrate"""
        for pattern in self.__general_ranks:
            ranks = self.__general_ranks[pattern]
            rank = ranks[0]  # TODO: support multi-rank for one pattern
            is_percentage = PERCENTAGE is rank.kind
            self.__general_percentage_count += rank.value if is_percentage else 0
            target_holder = self.__general_percentage_holder if is_percentage else self.__general_weight_holder
            assert pattern not in target_holder
            target_holder[pattern] = RankHolder(rank.value)
        assert self.__general_percentage_count <= 100

    def __get_current_timed_rank(self):
        """return percentage_rank_dict, weight_rank_dict (key: pattern, value: Rank)"""
        percentage_rank = {}
        weight_rank = {}
        for pattern in self.__timed_ranks:
            ranks = self.__timed_ranks[pattern]
            rank = ranks[0]  # TODO: support multi-rank for one pattern
            if rank.period.satisfy_current_time():
                target_rank = percentage_rank if PERCENTAGE is rank.kind else weight_rank
                target_rank[pattern] = rank
        return percentage_rank, weight_rank

    @staticmethod
    def __get_dice(general_holders, timed_ranks):
        """return a valid dice: dict within entry has 'rank' field"""
        import copy
        total_holders = copy.deepcopy(general_holders)
        for pattern in timed_ranks:
            assert pattern not in total_holders
            raw_rank = timed_ranks[pattern]
            # TODO: support multi-rank for one pattern
            rank = raw_rank[0] if isinstance(raw_rank, list) else raw_rank
            total_holders[pattern] = RankHolder(rank.value)
        return total_holders

    __HAS_SHOWN_PERCENTAGE_WARNING__ = False

    def arbitrate(self):
        """consider current date/time and value of the ranks, return the selected pattern"""
        timed_percentage_rank, timed_weight_rank = self.__get_current_timed_rank()
        timed_percentage_count = sum([timed_percentage_rank[pattern].value for pattern in timed_percentage_rank])
        total_percentage_count = self.__general_percentage_count + timed_percentage_count
        max_percentage = 100
        if total_percentage_count > max_percentage:
            max_percentage = total_percentage_count
            if not RankArbitrator.__HAS_SHOWN_PERCENTAGE_WARNING__:
                warning("total percentage count value '%s' is greater than 100" % total_percentage_count)
                RankArbitrator.__HAS_SHOWN_PERCENTAGE_WARNING__ = True
        dice = {PERCENTAGE: RankHolder(total_percentage_count),
                WEIGHT: RankHolder(max_percentage - total_percentage_count)}
        choice = get_weighted_random_dict_key(dice)
        general_holders = self.__general_percentage_holder if PERCENTAGE is choice else self.__general_weight_holder
        timed_ranks = timed_percentage_rank if PERCENTAGE is choice else timed_weight_rank
        if not general_holders and not timed_ranks:
            return None
        dice = self.__get_dice(general_holders, timed_ranks)
        choice_pattern = get_weighted_random_dict_key(dice)
        return choice_pattern


class Period(object):

    def __init__(self, period_str):
        self.month = None
        self.month_day = None
        self.week_day = None
        self.begin_time = None
        self.end_time = None
        self.empty = True
        self.parse(period_str)

    def parse(self, period_str):
        if not period_str:
            return
        self.empty = False
        for spec in period_str.split(','):
            # spec.: hhmm-hhmm
            if '-' in spec:
                [begin_time, end_time] = spec.split('-')
                assert 4 == len(begin_time) and 4 == len(end_time)
                begin_hour = int(begin_time[:2])
                begin_minute = int(begin_time[2:])
                end_hour = int(end_time[:2])
                end_minute = int(end_time[2:])
                assert begin_hour in range(24)
                assert end_hour in range(25)  # allow end_hour is 24
                assert begin_minute in range(60)
                assert end_minute in range(60)
                assert 24 != end_hour or 0 == end_minute
                self.begin_time = 60 * begin_hour + begin_minute
                self.end_time = 60 * end_hour + end_minute

    def __str__(self):
        return str(self.begin_time) + "-" + str(self.end_time) if not self.empty else ""

    def satisfy_current_time(self):
        assert self.begin_time is not None  # note: cannot use 'if self.begin_time', as begin_time can be 0
        from datetime import datetime
        today = datetime.today()
        cur_hour = today.hour
        cur_minute = today.minute
        cur_time = 60 * cur_hour + cur_minute
        cross_day = self.begin_time > self.end_time
        if cross_day:
            return cur_time > self.begin_time or cur_time < self.end_time
        else:
            return cur_time in range(self.begin_time, self.end_time)

KIND_KEY = "kind"
VALUE_KEY = "value"
PERIOD_KEY = "period"
PERCENTAGE_KEY = "PERCENTAGE"
WEIGHT_KEY = "WEIGHT"
RANK_KEY = "rank"  # this var is used in other module


class Rank(object):

    def __init__(self, kind, value, period):
        assert kind in [PERCENTAGE_KEY, WEIGHT_KEY]
        self.kind = PERCENTAGE if PERCENTAGE_KEY == kind else WEIGHT
        self.value = value
        self.period = Period(period)
        assert self.value > 0

    def print(self, prefix=None):
        print(prefix if prefix else '\t', WEIGHT_KEY if WEIGHT == self.kind else PERCENTAGE_KEY,
              self.value, self.period)

    @staticmethod
    def create(data=None):
        if not isinstance(data, dict):
            data = {}
        kind = data[KIND_KEY] if KIND_KEY in data else WEIGHT_KEY
        value = data[VALUE_KEY] if VALUE_KEY in data else 1
        period = data[PERIOD_KEY] if PERIOD_KEY in data else None
        return Rank(kind, value, period)

    @staticmethod
    def create_default():
        return Rank.create()
