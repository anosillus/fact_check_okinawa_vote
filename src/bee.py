#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: bee.py
# First Edit: 2022-10-25
# Last Change: 2022-10-25
a = 30
print(id(a))

for i in range(2):
    a = 50


print(a)
print(id(a))

# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
