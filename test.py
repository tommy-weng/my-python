#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import sys
import time
def foo():
    for i in range(5):
        sys.stdout.write("1111\n")
        #sys.stdout.flush()
        time.sleep(1)

if __name__ == "__main__":
    foo()
