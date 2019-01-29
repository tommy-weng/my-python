#!/usr/bin/python
# -*- coding: UTF-8 -*-

class Dfs:
    def __init__(self):
        self.m = 10
        self.n = 0
        self.dict = {}
        self.list = [0xFF for i in range(self.m)]
        self.flag = [False for i in range(self.m)]
        self.x = ""
        self.y = ""
        self.z = ""

    def get_digit(self):
        i = self.m -self.n
        for key in self.dict.keys():
            self.dict[key] = self.list[i]
            i += 1

    def find_equal(self):
        a = ""
        for i in self.x:
            a += self.dict[i]
        b = ""
        for i in self.y:
            b += self.dict[i]
        c = ""
        for i in self.z:
            c += self.dict[i]

        if (int(a) * int(b) == int(c)):
            print a + " * " + b + " = " + c

    def dfs(self, pos):
        if pos == self.m:
            self.get_digit()
            self.find_equal()
            return 
        for i in range(self.m):
            if self.flag[i] == False:
                self.list[pos] = str(i)
                self.flag[i] = True
                self.dfs(pos + 1)
                self.flag[i] = False

    def parse_formula(self, s):
        a = s.split('*')
        self.x = a[0].strip()
        b = a[1].split("=")
        self.y = b[0].strip()
        self.z = b[1].strip()

        for key in self.x + self.y + self.z:
            self.dict[key] = "0"
        self.n = len(self.dict)
        self.dfs(self.m - self.n)
if __name__ == "__main__":
    formula = "ABB * CD = EFGH"
    dfs = Dfs()
    dfs.parse_formula(formula) 
