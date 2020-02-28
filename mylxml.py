#!/usr/bin/python
# -*- coding: UTF-8 -*-

from lxml import etree as et

root = et.Element('html', version='5.0')

et.SubElement(root, 'head')
et.SubElement(root, 'title', bgcolor='red', fontsize='22')
et.SubElement(root, 'body', fontsize='15')

et.SubElement(root[1], 'test', fontsize='88')

root.text="html file"
root[2].text="I am in body"

#print content
print (et.tostring(root, pretty_print=True).decode('utf-8'))

#get elements
print(root[1].get('fontsize'))

# determine is an element
for i in range(len(root)):
    print(et.iselement(root[i]))

# get parent
print(root[0].getparent())

# get brothers
print(root[0].getnext())
print(root[1].getprevious())