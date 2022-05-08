#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Author sweng
Date   2017-12-22
"""

import sys
import time
def foo():
    for i in range(5):
        sys.stdout.write("1111\n")
        #sys.stdout.flush()
        time.sleep(1)

if __name__ == "__main__":
    foo()
