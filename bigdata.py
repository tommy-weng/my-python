__author__ = 'sweng'
# -*- coding: utf-8 -*-

with open('BigData_large_1509095761895', 'rb') as f:
    for line in f.readlines():
        inputdata = line.split(",")
        convertdata = [int(eval(item)) for item in inputdata]
        print str(sum(convertdata)).strip("L")