#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from base.setting.utility import Rank, RankArbitrator as Arbitrator, RANK_KEY
from util.json_load import JsonLoader

import sys
reload(sys)
sys.setdefaultencoding('UTF8')  # need this for str(pattern_of_type_unicode) can work


RESTRICT_KEY = "restrict"
DEFAULT_KEY = "default_value"


class Sentence(object):

    def __init__(self, rank, restrict, default_values):
        self.rank = rank
        self.__restrict = restrict
        self.__default_values = default_values

    def get_default_value(self, var_name):
        assert var_name in self.__default_values, "need specify default value of \'%s\' in phrase" % var_name
        return self.__default_values[var_name]

    def satisfy(self, pattern_name, pattern_group_name, file_base_name):
        if not self.__restrict:
            return True
        return self.__restrict in [pattern_name, pattern_group_name, file_base_name]

    def print(self):
        if self.rank:
            self.rank.print('\t\t')
        if self.__restrict:
            print('\t\t', self.__restrict)

    @staticmethod
    def create(data=None, global_restrict=None):
        if not data:
            return Sentence(Rank.create_default(), global_restrict, {})
        assert isinstance(data, dict)
        rank = Rank.create(data[RANK_KEY]) if RANK_KEY in data else Rank.create_default()
        restrict = str(data[RESTRICT_KEY]) if RESTRICT_KEY in data else global_restrict
        default_values = {}
        if DEFAULT_KEY in data:
            raw_data = data[DEFAULT_KEY]
            assert isinstance(raw_data, dict)
            for var_name in raw_data:
                default_values[var_name] = raw_data[var_name]
        return Sentence(rank, restrict, default_values)


TARGET_KEY = "target"
SENTENCE_KEY = "sentence"


class PhraseGroup(object):

    def __init__(self, name, targets, sentences, rank):
        assert isinstance(targets, list)
        assert isinstance(sentences, dict)
        self.name = str(name)  # raw pattern is of type 'unicode'
        self.targets = targets
        self.sentences = sentences
        self.rank = rank

    def get_default_value(self, sentence, var_name):
        assert sentence in self.sentences, "%s, %s" % (sentence, var_name)
        return self.sentences[sentence].get_default_value(var_name)

    def select_sentence(self, pattern, group_name, base_name):
        satisfied_sentences = []
        sentence_arbitrator = Arbitrator()
        for sentence in self.sentences:
            if self.sentences[sentence].satisfy(pattern, group_name, base_name):
                satisfied_sentences.append(sentence)
                sentence_arbitrator.add_rank(sentence, self.sentences[sentence].rank)
        sentence_arbitrator.finalize_rank()
        return sentence_arbitrator.arbitrate()

    def print(self):
        print(self.name)
        for target in self.targets:
            print('\t', target)
        self.rank.print()
        for sentence in self.sentences:
            print('\t', sentence)
            self.sentences[sentence].print()

    @staticmethod
    def create(name, data):
        assert isinstance(data, dict)
        targets = []
        sentences = {}
        rank = Rank.create(data[RANK_KEY]) if RANK_KEY in data else None
        if not rank:
            rank = Rank.create()
        if TARGET_KEY in data:
            raw_data = data[TARGET_KEY]
            if isinstance(raw_data, unicode):
                targets.append(raw_data)
            else:
                assert isinstance(raw_data, list)
                for target in raw_data:
                    targets.append(target)
        if SENTENCE_KEY in data:
            raw_data = data[SENTENCE_KEY]
            if isinstance(raw_data, dict):
                for sentence in raw_data:
                    sentences[sentence] = Sentence.create(raw_data[sentence])
            elif isinstance(raw_data, list):
                for sentence in raw_data:
                    sentences[sentence] = Sentence.create()
        if RESTRICT_KEY in data:
            raw_data = data[RESTRICT_KEY]
            assert isinstance(raw_data, dict)
            for restrict in raw_data:
                sentence_data = raw_data[restrict]
                if isinstance(sentence_data, list):
                    for sentence in sentence_data:
                        sentences[sentence] = Sentence.create(None, restrict)
                elif isinstance(sentence_data, dict):
                    for sentence in sentence_data:
                        sentences[sentence] = Sentence.create(sentence_data[sentence], restrict)
                else:
                    assert False
        return PhraseGroup(name, targets, sentences, rank)

GLOBAL_KEY = "global"


class SettingLoader(object):
    """load the phrase setting from json files"""

    def __init__(self, in_file=None, in_sentences=None):
        self.phrases = {}
        self.load_setting(in_file, in_sentences)

    def load_setting(self, in_file, in_sentences):
        assert bool(in_file) ^ bool(in_sentences)
        if in_sentences:
            self.phrases[GLOBAL_KEY] = PhraseGroup.create(GLOBAL_KEY, {SENTENCE_KEY: in_sentences})
            return
        json_data = JsonLoader(in_file).get_json_data()
        for phrase_group_name in json_data:
            self.phrases[phrase_group_name] = PhraseGroup.create(phrase_group_name, json_data[phrase_group_name])

    def print(self):
        for phrase_group_name in self.phrases:
            self.phrases[phrase_group_name].print()

if __name__ == '__main__':
    OBJ = SettingLoader("test_phrase.json")
    OBJ.print()
