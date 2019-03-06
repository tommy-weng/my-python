#!/usr/bin/python
import datetime
import re
import urllib2

def parse_item(html):
    tds = re.findall('<td>(.*?)</td>', html)
    match = re.match('<a href="?https://ullteb09.emea.nsn-net.net:8092/(\d+)"?>.*</a>', tds[2])
    id = match.group(1)
    return datetime.datetime.strptime(tds[1], "%Y-%m-%d"), id

def fetch_webpage(url):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    result = opener.open(url)
    return result.read()

def get_trs_from_whole_webpage(html):
    trs = re.findall('<tr .*?>.*?</tr>', html)
    return trs

def get_all_commits(html):
    trs = get_trs_from_whole_webpage(html)
    commits = {}
    for tr in trs:
        d, idx = parse_item(tr)
        commits[idx] = d
    return commits

def load_html_file(fname):
    f = open(fname)
    html = f.read().replace('\n', '')
    return html

if __name__ == "__main__":
    pass