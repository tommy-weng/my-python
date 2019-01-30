#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Author sweng
Date   2017-12-22
"""
import sys, getopt
import re
from hello import Hello

class Testx:
    def __init__(self, string, pattern):
        self.string = string 
        self.pattern = pattern
        self.lines = []

    def my_print(self):
        print "Matched %d lines."% len(self.lines)
        for line in self.lines:
            print line.group()
        
    def my_match(self):
        lines = re.finditer(r"%s"%self.pattern, self.string, re.DOTALL)
        self.lines = [item for item in lines]
        
    def my_getopt(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "s:p:", ["string=","pattern="])
        except getopt.GetoptError:
            print 'Usage: %s [-s|--pattern] <string> [-p|--pattern] <pattern>' % (sys.argv[0])
            exit(2)
 
        for opt, arg in opts:
            if opt == '-s':
                self.string = arg
            elif opt == '-p':
                self.pattern = arg
                
def my_function(arg, *var_tuple, **var_dict):
    print arg
    print var_tuple
    print var_dict
    for var in var_tuple:
        print var
    for key, value in var_dict.items():
        print key, value
    
sum = lambda a, b: a + b
    
if __name__ == "__main__":
    my_function(1,2,3,4,age='1',name='tommy')
