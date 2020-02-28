#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import matplotlib.pyplot as plt

keys=['time', 'grpid', 'datatype', 'predictload']

with open('tensorflow_powersaving_bts_x86.log', 'rb') as f:
    # print f.readline()
    # lines = f.readlines()
    lines = f.read().splitlines()
    # print lines
    gbr = []
    nongbr=[]
    pdcch = []
    for line in lines:
        # print (line)
        values = str(line).split(",")
        d = dict(zip(keys, values))
        d['datatype'] = d['datatype'].split('=')[1]
        d['predictload'] = re.split(r'\[|\]', (d['predictload'].split('=')[1]))[1].strip()
        # print (d)
        if d['datatype'] == '0':
          gbr.append(d['predictload'])
        elif d['datatype'] == '1':
          nongbr.append(d['predictload'])
        else:
          pdcch.append(d['predictload'])
    #print (gbr, nongbr, pdcch)
    
    plt.plot(gbr, label='gbr')
    plt.plot(nongbr, label='nongbr')
    plt.plot(pdcch, label='pdcch')
    
    plt.xlabel('time')
    plt.ylabel('load')
    plt.legend()
    plt.show()