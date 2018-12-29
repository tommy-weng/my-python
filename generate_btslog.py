#!/bin/python

import sys

def generate_btslog():
    if (len(sys.argv) != 3):
        print "Usage: %s <infile> <outfile> " % sys.argv[0]
        return
    print "infile: " + sys.argv[1] + ", outfile: " + sys.argv[2]
    
    #strip_control_characters = lambda s:"".join(i for i in s if ord(i) != 0)
    strip_control_characters = lambda s:"".join(i for i in s if i != '\0')
    
    with open(sys.argv[1], 'rb') as infile:
       
        outfile = open(sys.argv[2], 'wb')
        for line in infile.readlines():
            outline = strip_control_characters(line)
            outfile.writelines(outline)
        outfile.close()

if __name__ == "__main__":
    generate_btslog()