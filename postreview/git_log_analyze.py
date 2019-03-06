#!/usr/bin/python
import os
import json
import re
import subprocess
from datetime import datetime

class Commit(object):
    class Rollback():
        rollback_info = {}
        start = 0
        end = 0
        def is_revert_commit(self, lines):
            '''check whether this commit is for revert other commit(s)'''
            match = re.match('^commit (.*)', lines[0])
            sha1 = match.group(1)

            match = re.match(r'^\s+DESCRIPTION: roolback by CI from (\d+) to (\d+)', lines[6])
            if match:
                self.rollback_info[sha1] = [int(match.group(2)), int(match.group(1))]
                return True

            match = re.match(r'^\s+This reverts commit ([0-9a-f]+).', lines[6])
            if match:
                self.rollback_info[sha1] = match.group(1)
                return True

            return False

        def has_rollbacked(self, commit, rev):
            '''Check whether this commit has been rollbacked'''
            for (sha1, item) in self.rollback_info.items():
                if isinstance(item, str):
                    if item == commit:
                        print "%s is rollbacked by %s." % (commit, sha1)
                        return sha1
                else:
                    if item[0] < rev and rev <= item[1]:
                        print "%s is rollbacked by %s." % (commit, sha1)
                        return sha1
            return None

    rollback = Rollback()
    accounts_info = {
        'qiliang' : ["Liang, Qingquan", "Titan"],
        'yugqiao' : ["Qiao, Yuguo", "Titan"],
        'f1shi' : ["Shi, Feng 2.", "Titan"],
        'lintu' : ["Tu, Linggang", "Titan"],
        'dbgn37' : ["Zhang, Hui Tuan", "Titan"],
        'gpx736' : ["Zhang, Shuyan", "Titan"],
        'yawzheng' : ["Zheng, Yawei", "Titan"],
        'minwang' : ["Wang, Min 1.", "Titan"],
        'z3li' : ["Li, Zhi", "Titan"],
        'kding' : ["Ding, Ke", "Voyager"],
        'tinggao' : ["Gao, Ting 2.", "Voyager"],
        'jijumeng' : ["Meng, Jijun J.", "Voyager"],
        'sweng' : ["Weng, Shiqiang", "Voyager"],
        'chunyxu' : ["Xu, Chunyan", "Voyager"],
        'cxrp34' : ["Zeng, Gaelen", "Voyager"],
        'guangzhu' : ["Zhu, Guang", "Voyager"],
        'rohuang' : ["Huang, Roy", "Voyager"]
        }
    fb_info = [ datetime.strptime(date_str, '%Y-%m-%d') for date_str in ['2015-12-16', 
        '2016-01-20', '2016-02-24', '2016-03-23', '2016-04-27', '2016-05-25', '2016-06-22', 
        '2016-07-27', '2016-08-24', '2016-09-28', '2016-10-26', '2016-11-23', '2016-12-21', 
        '2017-1-31', '2017-2-28', '2017-3-28', '2017-4-25', '2017-5-23', '2017-6-20', '2017-7-25', '2017-8-29', '2017-9-26', '2017-10-24', '2017-11-21', '2017-12-19', 
        '2018-1-25', '2018-2-14', '2018-3-24', '2018-4-24']]

    def __init__(self, lines):
        self.info = {'changes':[]}
        #commit
        match = re.match('^commit (.*)', lines[0])
        self.info['sha1'] = match.group(1)

        match = re.match('^Merge: .*', lines[1])
        if match:
            raise UserWarning("%s is a merge node" % self.info['sha1'])

        if self.rollback.is_revert_commit(lines):
            raise UserWarning("%s is rollback commit" % self.info['sha1'])

        #author
        match = re.match('^Author: (.*) <.*>', lines[1])
        self.info['author'] = match.group(1)

        if self.info['author'] not in self.accounts_info:
            raise UserWarning()

        #date
        match = re.match(r'Date:\s+([\-0-9]{10} [:0-9]{8}) \+0800', lines[2])
        self.info['date'] = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')

        #title
        match = re.match(r'^\s+(.*)', lines[4])
        self.set_title(match.group(1))
        '''
        for line in lines:
            # svn info
            match = re.match(r'^\s+git-svn-id:.*/svnroot/([^/]+)(/|/.*/)([^/]+)@(\d+) .*', line)
            if match:
                self.info['branch'] = match.group(3)
                self.info['svn'] = int(match.group(4))

            # change-id
            match = re.match('^\s+Change-Id:\s*(I[0-9a-f]{40})', line)
            if match:
                self.info['change-id'] = match.group(1)

            # change files
            match = re.match(r'^(\d+)\s+(\d+)\s+(.*)', line)
            if match:
                fname = match.group(3)
                if fname.find('opt_tti_trace_parser_tdd') != -1:
                    continue  #ignore auto generated files

                if fname[-4:] == '.rtm':
                    ftype = 'rtm'
                else:
                    ftype = 'code'

                self.info['changes'].append({'add':int(match.group(1)), 'del':int(match.group(2)), 'file':fname, 'ftype':ftype})

        # it's from svn commit
        if 'change-id' not in self.info:
            self.info['change-id'] = ''

        # it's not in svn system
        #if 'svn' not in self.info:
        #    self.info['svn'] = 0
        #    self.info['branch'] = ''

        self.info['rollbacked'] = self.rollback.has_rollbacked(self.info['sha1'], self.info['svn'])
        '''
        #extra elements
        self.info['fullname'] = self.accounts_info[self.info['author']][0]
        self.info['team'] = self.accounts_info[self.info['author']][1]
        #self.info['fb'] = self.get_fb(self.info['date'])


    def set_title(self, title):
        if title[0:8] == 'FEATURE:':
            title = title[8:]
        commit_type = title[0:2]
        if commit_type == 'NF' or  commit_type == 'PR':
            match = re.match('(NF|PR)\s+([^:]+):(.*)', title)
            if match:
                self.info['feature'] = match.group(2)
                self.info['title'] = match.group(3)
            else:
                print "Wrong format: '%s'" % title
                self.info['feature'] = ""
                self.info['title'] = title[3:]
            self.info['type'] = commit_type
        elif commit_type == 'IN':
            self.info['feature'] = ""
            self.info['title'] = title[3:]
            self.info['type'] = commit_type
        else:
            #FDD free mode
            match = re.match(r'(LTE[\d]+(?:-[A-Z]-[a-z0-9]+)?)[:\s]+(.*)', title)
            if match:
                self.info['feature'] = match.group(1)
                self.info['title'] = match.group(2)
                self.info['type'] = 'NF'
            else:
                self.info['feature'] = ''
                self.info['title'] = title
                self.info['type'] = 'IN'

    def get_fb(self, d):
        for i in range(0, len(self.fb_info)):
            if d >= self.fb_info[i] and d < self.fb_info[i + 1]:
                return "fb%02d%02d" % (self.fb_info[i + 1].year % 100, i % 12 + 1)

class AllCommits(object):
    '''container for all commits'''
    def __init__(self, fname):
        self.commits = []
        commit_message = []
        for line in open(fname):
            if re.match('^commit .*', line):
                self.insert_new_commit(commit_message)
                commit_message = []
            commit_message.append(line)
        self.insert_new_commit(commit_message)

    def insert_new_commit(self, commit_message):
        '''add a new commit to container'''
        if len(commit_message) > 0:
            try:
                commit = Commit(commit_message)
                self.commits.append(commit)
            except UserWarning, err:
                pass

if __name__ == "__main__":
    gitlog = AllCommits("tddps-trunk.log")
      
    for commit in gitlog.commits:
        print commit.info['sha1'], commit.info['author'], commit.info['date']
