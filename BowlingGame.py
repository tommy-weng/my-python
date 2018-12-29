__author__ = 'sweng'
# -*- coding: utf-8 -*-

def get_ball_score(ball):
    if ball == '-':
        return 0
    elif ball == 'X':
        return 10
    return int(eval(ball))

def get_curr_frame_score(frame):
    if frame[0] == 'X' or frame[1] == '/':
        return 10
    if frame[0] == '-' and frame[1] == '-':
        return 0
    if frame[0] == '-':
        return int(eval(frame[1]))
    if frame[1] == '-':
        return int(eval(frame[0]))
    return int(frame[0]) + int(frame[1])

def calc_score_frame_sum(frames, index):
    currframe = frames[index]
    score = get_curr_frame_score(currframe)
    if currframe[0] == 'X':
        nextframe1 = frames[index + 1]
        score += get_curr_frame_score(nextframe1)
        if nextframe1[0] == 'X':
            nextframe2 = frames[index + 2]
            score += get_ball_score(nextframe2[0])
    elif score == 10:
        nextframe = frames[index + 1]
        score += get_ball_score(nextframe[0])

    return score

def calc_score_previous_8_frame(frames):
    score = 0
    for index in range(len(frames)):
        if index < 8:
            score += calc_score_frame_sum(frames, index)
    return score

def calc_score_9th_frame(currframe, nextframe, addition):
    score = get_curr_frame_score(currframe)
    if currframe[0] == 'X':
        score += get_curr_frame_score(nextframe)
        if nextframe[0] == 'X':
            score += get_ball_score(addition[0])
    elif score == 10:
        score += get_ball_score(nextframe[0])
    return score

def calc_score_addition(addition):
    score = 0
    for item in addition:
        score += get_ball_score(item)
    return score

def calc_score_10th_frame(frame, addition):
    return get_curr_frame_score(frame) + calc_score_addition(addition)

def excute(file):
    with open(file, 'rb') as f:
        for linenum, line in enumerate(f):
            if linenum == 0:
                continue
            input = line.split("||")
            base = input[0].split("|")
            addition = ''
            if len(input) > 1:
                addition = input[1].strip("\r\n")

            score = calc_score_previous_8_frame(base) + \
                    calc_score_9th_frame(base[8], base[9], addition) + \
                    calc_score_10th_frame(base[9], addition)

            print score

if __name__ == '__main__':
    excute("BowlingGame_large_1509436882752")


