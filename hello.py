#!/usr/bin/python



import re

class Hello:
    name = []
    salary = 0
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def print_module(self):
        print __name__
    def showx(self):
        print "name:%s, salary:%d" % (self.name, self.salary)


if __name__ == "__main__":
    print "Start: %s" % "xx"
    t = Hello("Tommy", 10)
    print t.showx

