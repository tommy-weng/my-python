#!/usr/bin/python

count = 0

def count_off(start, num):
    if (1 == num):
        return
    global count
    offset = start - 1
    candidate = []
    for i in range(num):
        candidate.append((i + offset) % 3 + 1)
    remain = num;
    for c in candidate:
        if (3 == c):
            remain -= 1
    if (2 == num and 3 == candidate[0]):
        num = 1    
    count += num
    print num, candidate[num - 1]
    count_off(candidate[num - 1] % 3 + 1, remain)
if __name__ == "__main__":
    count_off(1, 30)
    print count
