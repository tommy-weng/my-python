__author__ = 'sweng'
# -*- coding: utf-8 -*-

def excute(file):
    with open(file, 'rb') as f:
        caseNum = 0
        line1 = []
        line2 = []
        for linenum, line in enumerate(f):
            if linenum == 0:
                continue
            inputData = line.split(' ')
            satisfied = 0
            if linenum % 2 == 1:
                line1 = inputData
            else:
                caseNum += 1
                line2 = inputData
                candyNum = int(line1[1])
                if candyNum == 2:
                    notSatisfiedList = []
                    for person in line2:
                        remain = int(eval(person)) % 2
                        if remain % 2 == 0:
                            satisfied += 1
                        else:
                            notSatisfiedList.append(remain)
                    listLen = len(notSatisfiedList)
                    satisfied += listLen / 2 + listLen % 2

                if candyNum == 3:
                    len1 = 0; len2 = 0
                    for person in line2:
                        remain = int(eval(person)) % 3
                        if remain == 0:
                            satisfied += 1
                        elif remain == 1:
                            len1 += 1
                        else:
                            len2 += 1
                    minLen = min(len1, len2)
                    maxLen = max(len1, len2)
                    diffLen = maxLen - minLen
                    satisfied += minLen + diffLen / 3 + int(1 if diffLen % 3 else 0)

                if candyNum == 4:
                    num1 = 0; num2 = 0; num3 = 0
                    for person in line2:
                        remain = int(eval(person)) % 4
                        if remain == 0:
                            satisfied += 1
                        elif remain == 1:
                            num1 += 1
                        elif remain == 2:
                            num2 += 1
                        else:
                            num3 += 1
                    minNum = min(num1, num3)
                    maxNum = max(num1, num3)
                    diff = maxNum - minNum
                    tempDiff = diff
                    remain2 = num2 % 2
                    if remain2 == 1:
                        tempDiff = 0 if diff < 3 else diff - 2

                    satisfied += minNum + num2 / 2  + remain2 + tempDiff / 4 + int(1 if tempDiff % 4 else 0)

                print("Case #%u: %u" % (caseNum, satisfied))

if __name__ == '__main__':
    excute("Candy_large_1509608769644")