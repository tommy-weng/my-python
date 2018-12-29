__author__ = 'sweng'
# -*- coding: utf-8 -*-

def excute(file):
    with open(file, 'rb') as f:
        for linenum, line in enumerate(f):
            if linenum == 0:
                print int(line)
                continue
            book = [0,0,0,0,0]
            group = [0,0,0,0,0]
            for item in line:
                if item == '1':
                    book[0] += 1
                if item == '2':
                    book[1] += 1
                if item == '3':
                    book[2] += 1
                if item == '4':
                    book[3] += 1
                if item == '5':
                    book[4] += 1

            book.sort()
            diff = book[2] - book[1]
            diff = min(diff, book[0])

            group[4] = book[0] - diff
            group[3] = book[1] + diff - group[4]
            group[2] = book[2] - (book[1] + diff)
            group[1] = book[3] - book[2]
            group[0] = book[4] - book[3]
            sum = 8 * (group[0] + group[1] * 2 * 0.95 + group[2] * 3 * 0.9 + group[3] * 4 * 0.8 + group[4] * 5 * 0.75)
            print str(sum).strip('0').strip('.')


if __name__ == '__main__':
    excute("DaoMuBook_large_1509525324710")