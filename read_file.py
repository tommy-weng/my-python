#!/usr/bin/python
# -*- coding: UTF-8 -*-

keys=['time', 'grpid', 'gbr', 'nongbr', 'pdcch']

with open('tensorflow_powersaving_training.log', 'rb') as f:
    #print f.readline()
    # lines = f.readlines()
    lines = f.read().splitlines()
    #print lines

    list1=[]
    list2=[]

    gbr1=[]
    nongbr1=[]
    pdcch1=[]

    gbr2=[]
    nongbr2=[]
    pdcch2=[]
    
    count = 96
    for line in lines:
        #print (line)
        values = line.split(",")
        d = dict(zip(keys, values))
        
        #if d['time'][7:9] !='16' or count == 0:
        #    continue

        if d['grpid'] == '0':
            count = count - 1
            gbr1.append(float(d['gbr']))
            nongbr1.append(float(d['nongbr']))
            pdcch1.append(float(d['pdcch']))
        else:
            gbr2.append(float(d['gbr']))
            nongbr2.append(float(d['nongbr']))
            pdcch2.append(float(d['pdcch']))
    list1.append(gbr1)
    list1.append(nongbr1)
    list1.append(pdcch1)
    
    list2.append(gbr2)
    list2.append(nongbr2)
    list2.append(pdcch2)
    print (len(gbr1), len(pdcch1))
    print (list1, list2)
        # convertdata = [int(eval(item)) for item in inputdata]
        # print str(sum(convertdata)).strip("L")