__author__ = 'sweng'
# -*- coding: utf-8 -*-

def build_road_mark(sheet, roadMark):
    maxRow = len(sheet)
    maxColumn = len(sheet[0])
    person = [0, 0]
    for i in range(maxRow):
        col = []
        for j in range(maxColumn):
            if sheet[i][j] == 'Z':
                person = [i, j]
            up = 0;down = 0;left = 0;right = 0
            if sheet[i][j] == '.' or sheet[i][j] == 'Z':
                if i == 0:
                    up = 1
                if i == maxRow - 1:
                    down = 1
                if j == 0:
                    left = 1
                if j == maxColumn - 1:
                    right = 1

                if i > 0:
                    if sheet[i - 1][j] == '*':
                        up = 1
                    elif sheet[i - 1][j] == 'L':
                        up = 2
                if i < maxRow - 1:
                    if sheet[i + 1][j] == '*':
                        down = 1
                    elif sheet[i + 1][j] == 'L':
                        down = 2
                if j > 0:
                    if sheet[i][j - 1] == '*':
                        left = 1
                    elif sheet[i][j - 1] == 'L':
                        left = 2
                if j < maxColumn - 1:
                    if sheet[i][j + 1] == '*':
                        right = 1
                    elif sheet[i][j + 1] == 'L':
                        right = 2

            pos = [up, down, left, right]
            col.append(pos)
        roadMark.append(col)
        col = []
    return person

def calc_time(sheet):
    roadMark = []
    person = build_road_mark(sheet, roadMark)
    i = person[0];
    j = person[1]
    step = 0
    stack = []
    while (1):
        mark = roadMark[i][j]
        roadCount = 0
        arrived = 0
        for index in range(len(mark)):
            if mark[index] == 2:
                arrived = 1;
                break
            if mark[index] == 0:
                roadCount += 1
        if arrived == 1:
            step += 1;
            break
        if roadCount > 1:
            pos = [i, j, step]
            stack.append(pos)
        maxRow = len(sheet)
        maxCol = len(sheet[0])
        if mark[0] == 0:
            if i > 0:
                roadMark[i][j][0] = 1
                i -= 1;
                step += 1
                roadMark[i][j][1] = 1
        elif mark[1] == 0:
            if i < maxRow - 1:
                roadMark[i][j][1] = 1
                i += 1;
                step += 1
                roadMark[i][j][0] = 1
        elif mark[2] == 0:
            if j > 0:
                roadMark[i][j][2] = 1
                j -= 1;
                step += 1
                roadMark[i][j][3] = 1
        elif mark[3] == 0:
            if j < maxCol - 1:
                roadMark[i][j][3] = 1
                j += 1;
                step += 1
                roadMark[i][j][2] = 1
        else:
            if len(stack) == 0:
                step = 0;
                break
            pos = stack.pop()
            i = pos[0];
            j = pos[1];
            step = pos[2]
    return step

def excute(file):
    with open(file, 'rb') as f:
        caseIndex = 0
        infoLine = 1
        sheet = []
        time = 0
        for linenum, line in enumerate(f):
            if linenum == 0:
                continue
            if linenum == infoLine:
                info = line.split(' ')
                height = int(eval(info[1]))
                time = int(eval(info[2]))
                infoLine += height + 1
                caseIndex += 1
            else:
                list = line.strip(' \r\n').split(' ')
                sheet.append(list)

            if linenum == infoLine - 1:
                costTime = calc_time(sheet)
                if costTime > time or costTime == 0:
                    print("Case #%u: NO" % caseIndex)
                else:
                    print("Case #%u: YES" % caseIndex)
                sheet = []


if __name__ == '__main__':

    excute("LongMenHotel_large_1509703990827")