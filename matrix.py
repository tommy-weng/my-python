#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
def foo():
    a = np.mat([[1,2],[3,4]])
    print(a)
    print(a.T)
    print(a.I)
    b = np.mat(np.eye(2,2)*0.5)
    print(b.I)

if __name__ == "__main__":
    foo()
