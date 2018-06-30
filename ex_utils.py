#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""


def _redirect_lookup_table(value):
    if 'a' in value:   return "/a/"
    elif 'b' in value: return "/b/"
    elif 'c' in value: return "/c/"
    elif 'd' in value: return "/"
    else: return None