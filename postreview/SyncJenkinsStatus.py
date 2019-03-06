#!/usr/bin/python
import urllib
import urllib2
import codecs
import string
import cookielib
import re
import MySQLdb
import datetime


     
class Jenkins:
    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.login()

    def login(self):
        loginUrl = 'http://hztddgit.china.nsn-net.net/jenkins/j_acegi_security_check'
        postdata = urllib.urlencode({
            'j_username':self.account,
            'j_password':self.password,
            'from':'/jenkins/',
            'json':str({"j_username": self.account, "j_password": self.password, "remember_me": 'false', "from": "/jenkins/"}),
            'Submit':'login'
            })
        filename = 'cookie.txt'
        self.cookie = cookielib.MozillaCookieJar(filename)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.opener.open(loginUrl, postdata)

    def get(self, url):
        result = self.opener.open("http://hztddgit.china.nsn-net.net/jenkins/gerrit-trigger/diagnostics/buildMemory/")
        return result.read()

class HtmlParser:
    def _convert_data(self, s):
        if len(s) == 0:
            return None
        else:
            if s.find('/') != -1:
                #3/7/17 6:26:31 PM
                return datetime.datetime.strptime(s, "%m/%d/%y %I:%M:%S %p")
            else:
                #2017-03-07 18:26:31
                return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    def RemoveFormat(self, s):
        if len(s) == 0:
            return None
        else:
            m = re.match('<.*>(.*?)</.*>', s)
            return m.group(1)
    def do(self, html):
        content = html.replace('\n', '')
        match = re.match('.*<table class="sortable pane bigtable">(.*?)</table>.*', content)
        table = match.group(1)
        allJobs = []
        patchset_info = {}
        for item in re.finditer('<tr>(.*?)</tr>', table):
            text = item.group(1).replace('&nbsp;', '')
            if text.find('<th id="hJob" align="left">') != -1:
                continue # head line
            if not self._parse_patchset_line(text, patchset_info):
                job = self._parse_one_row(text)
                job.update(patchset_info)
                allJobs.append(job)
        return allJobs

    def _parse_patchset_line(self, text, contents):
        match = re.match('<th .*?>patchset-created (\d+)/(\d+) @ (.*)\+0800</th>', text)
        if match:
            contents['number'] = match.group(1)
            contents['patchset'] = match.group(2)
            contents['created'] = self._convert_data(match.group(3))
            return True
        else:
            return False

    def _parse_one_row(self, text):
        job = {}
        tds = re.findall('<td .*?>(.*?)</td>', text)
        match = re.match('<a href="(.*?)">(.*?)</a>', tds[0])
        job['job'] = match.group(2)
        job['job_url'] = match.group(1)
        match = re.match('<a href="(.*?)">(.*?)</a>', tds[1])
        if match:
            job['build'] = match.group(2)
            job['build_url'] = match.group(1)
        else:
            job['build'] = None
            job['build_url'] = None
        job['iscompleted'] = self.RemoveFormat(tds[2])
        job['result'] = self.RemoveFormat(tds[3])
        job['triggered'] = self._convert_data(tds[4])
        job['started'] = self._convert_data(tds[5])
        job['completed'] = self._convert_data(tds[6])
        return job

class MyDB:
    def __init__(self, dbname, table):
        self.table = table
        self.db = MySQLdb.connect("10.56.78.54","tvd","tvd1234", dbname, charset="utf8")
        self.cursor = self.db.cursor()

    def write(self, contents, keys):
        remain_contents, conditions = self._split_contents_by_keys(contents, keys)
        if self._is_existed(conditions):
            self._update(remain_contents, conditions)
        else:
            self._insert(contents)

    def _is_existed(self, conditions):
        sql, values = self._format_select_sentence(conditions)
        count = self.cursor.execute(sql, values)
        return count != 0

    def _insert(self, contents):
        sql, values = self._format_insert_sentence(contents)
        self._excute_sql_sentence(sql, values)
    
    def _format_insert_sentence(self, contents):
        keys_tuple = ()
        values_tuple = ()
        for (k, v) in contents.items():
            keys_tuple += (k,)
            values_tuple += (v,)
        sql = "INSERT INTO " + self.table + " (" + ','.join(map(str, keys_tuple)) + ") VALUES (" + ','.join(['%s']*len(values_tuple))  + ")"
        return sql, values_tuple

    def _excute_sql_sentence(self, sql, values):
        self.cursor.execute(sql, values)
        self.db.commit()

    def _convert_to_tuple(self, contents):
        conditions = []
        values_tuple = ()
        for (k, v) in contents.items():
            conditions.append('%s=%%s' % k)
            values_tuple += (v,)
        return conditions, values_tuple
        
    def _format_select_sentence(self, keys):
        conditions, values_tuple = self._convert_to_tuple(keys)
        sql = "SELECT * FROM " + self.table + " WHERE " + ' AND '.join(conditions)
        return sql, values_tuple

    def _split_contents_by_keys(self, contents, keys):
        remain_contents = dict(contents)
        conditions = {}
        for k in keys:
            conditions[k] = remain_contents[k]
            del remain_contents[k]
        return remain_contents, conditions

    def _format_update_sentence(self, contents, conditions):
        set_params, values1 = self._convert_to_tuple(contents)
        where_params, values2 = self._convert_to_tuple(conditions)
        sql = "UPDATE " + self.table + " SET " + ','.join(set_params) + " WHERE " + ','.join(where_params)
        return sql, values1 + values2
    
    def _update(self, contents, conditions):
        sql, values = self._format_update_sentence(contents, conditions)
        self._excute_sql_sentence(sql, values)
    
    def _remove_record(self, conditions):
        sql_conditions, values = self._convert_to_tuple(conditions)
        sql = "DELETE FROM " + self.table + " WHERE " + ' AND '.join(sql_conditions)
        self._excute_sql_sentence(sql, values)

if __name__ == "__main__":
    f = open("output2.txt")
    html = f.read()
    parser = HtmlParser()
    allJobs = parser.do(html)
    print allJobs
    db = MyDB("gerritci")
    for job in allJobs:
        db.write(job, ['build_url'])
