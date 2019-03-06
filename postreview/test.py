#!/usr/bin/python

import codecs

import re

f = codecs.open("a.html", "r", "utf-8")
txt = f.read()

f.close()
line = re.search(r'<span class="commit-author-name">(\w+)</span>', txt)

print txt
print line.group(0)
print line.group(1)
