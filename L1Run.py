#!/usr/bin/env python
# encoding: utf-8

# File        : L1Run.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2018 Apr 04
#
# Description : A class for holding information of each run


class L1Run():
    def __init__(self, run, Type):
        self.runNumber = run
        self.runType = Type
        self.startTime = None
        self.stopTime = None
        self.startLS = None
        self.stopLS = None
        self.fill = None
        self.keys = {}

    def AddKeys(self, k, v):
        self.keys[k] = v




