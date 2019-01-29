#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Author sweng
Date   2017-12-22
"""

def foo(i):
    if i == 0:
        print True
    elif i == 1:
        print False
        return
    else:
        print 2

if __name__ == "__main__":
    foo(2)
