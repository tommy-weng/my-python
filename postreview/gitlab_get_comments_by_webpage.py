#!/usr/bin/python
import urllib
import urllib2
import re
import codecs
import string
import json
from datetime import datetime, timedelta
from HTMLParser import HTMLParser

class Gitlab(object):
    project_map = {'tddps':'2617', 'fddps':'2663'}
    accounts_info = {
        'qiliang' : ["Liang, Qingquan", "Titan"],
        'yugqiao' : ["Qiao, Yuguo", "Titan"],
        'f1shi' : ["Shi, Feng 2.", "Titan"],
        'lintu' : ["Tu, Linggang", "Titan"],
        'dbgn37' : ["Zhang, Hui Tuan", "Titan"],
        'gpx736' : ["Zhang, Shuyan", "Titan"],
        'yawzheng' : ["Zheng, Yawei", "Titan"],
        'kding' : ["Ding, Ke", "Voyager"],
        'tinggao' : ["Gao, Ting 2.", "Voyager"],
        'jijumeng' : ["Meng, Jijun J.", "Voyager"],
        'sweng' : ["Weng, Shiqiang", "Voyager"],
        'chunyxu' : ["Xu, Chunyan", "Voyager"],
        'cxrp34' : ["Zeng, Gaelen", "Voyager"],
        'guangzhu' : ["Zhu, Guang", "Voyager"],
        'minwang' : ["Wang, Min 1.", "Titan"],
        'z3li' : ["Li, Zhi", "Titan"],
        'rohuang' : ["Huang, Roy", "Voyager"]
        }

    accounts_info_new = {
        'Liang Qingquan' : ["Liang, Qingquan", "Titan"],
        'Qiao Yuguo' : ["Qiao, Yuguo", "Titan"],
        'Shi Feng' : ["Shi, Feng 2.", "Titan"],
        'Tu linggang' : ["Tu, Linggang", "Titan"],
        'Zhang Hui Tuan' : ["Zhang, Hui Tuan", "Titan"],
        'Zhang Shuyan' : ["Zhang, Shuyan", "Titan"],
        'Zheng Yawei' : ["Zheng, Yawei", "Titan"],
        'Ding Ke' : ["Ding, Ke", "Voyager"],
        'Ting 2. Gao' : ["Gao, Ting 2.", "Voyager"],
        'Meng Jijun' : ["Meng, Jijun J.", "Voyager"],
        'Weng Shiqiang-Tommy' : ["Weng, Shiqiang", "Voyager"],
        'Xu Chunyan' : ["Xu, Chunyan", "Voyager"],
        'Gaelen Zeng' : ["Zeng, Gaelen", "Voyager"],
        'Zhu Guang' : ["Zhu, Guang", "Voyager"],
        'Wang Min' : ["Wang, Min 1.", "Titan"],
        'Li Zhi' : ["Li, Zhi", "Titan"],
        'Huang Roy' : ["Huang, Roy", "Voyager"]
        }

    def __init__(self):
        self.commits_info = []

    def _remove_html_tags(self, text):
        for m in re.finditer('<p dir="auto">.*?</p>', text):
            ret = text[m.start() + 14:m.end() - 4]
            match = re.match('(.*?)<[^>]+>(.*?)</a>', ret)
            if match:
                ret = match.group(1) + match.group(2)
            return ret
        return ""

    def _get_fname(self, html):
        h = HTMLParser()
        html = h.unescape(html)
        data = json.loads(html)
        if data['new_line']:
            return [data['new_path'], data['new_line']]
        else:
            return [data['old_path'], data['old_line']]

    def _parse_notes_detail(self, note):
        ret = []
        #for m in re.finditer(r'<div class="note-headline-light">\n<span class="hidden-xs">\n@([\w\.]+)\n</span>\ncommented\n<a href="#(note_\d+)">\n<time class="js-timeago note-created-ago".*?datetime="([0-9T\-:]+)Z".*?<textarea [^>]+>(.*?)</textarea>', note, re.DOTALL):
        for m in re.finditer(r'<span class="note-headline-light">\n@([\w\.]+)\n</span>\n</a>\n<span class="note-headline-light">\n<span class="note-headline-meta">\ncommented\n<a href="#(note_\d+)">\n<time class="js-timeago note-created-ago".*?datetime="([0-9T\-:]+)Z".*?<textarea [^>]+>(.*?)</textarea>', note, re.DOTALL):
            info = {}
            info['author'] = m.group(1)
            info['id'] = m.group(2)
            info['date'] = datetime.strptime(m.group(3), '%Y-%m-%dT%H:%M:%S') + timedelta(hours=8) 
            info['note'] = m.group(4)
            ret.append(info)
        return ret

    def parse_html(self, project, commit):
        f = codecs.open("a.html", "r", "utf-8")
        html = f.read()
        f.close()
        
        sectors = html.split("<div class=\"diff-content\">")
        m = re.search(r'<span class="commit-author-name">(.+)</span>', sectors[0])
        author = m.group(1)
        if self.accounts_info.has_key(author):
            team = self.accounts_info[author][1]
        elif self.accounts_info_new.has_key(author):
            team = self.accounts_info_new[author][1]
        else:
            return
        for item in range(1, len(sectors)):
            lines = sectors[item].split("/tr")
            for i in range(1, len(lines)):
                m_pre_line = re.search(r'data-line-code="([0-9a-f_]+)" data-line-type="(?:new|old|null)" data-note-type="DiffNote" data-position="({[^}]+})"', lines[i-1], re.DOTALL)
                m_cur_line = re.search(r'<tr class="notes_holder">(.*)', lines[i], re.DOTALL)
                if None != m_cur_line:
                    note = {}
                    note['note'] = self._parse_notes_detail(m_cur_line.group(1))
                    note['ref'] = m_pre_line.group(1)
                    note['fname'] = self._get_fname(m_pre_line.group(2))
                    note['author'] = author
                    note['team'] = team
                    note['project'] = project
                    note['sha1'] = commit
                    self.commits_info.append(note)
    
    def fetch_commit_html(self, project, commit):
        loginUrl = 'http://gitlabe1.ext.net.nokia.com/lte/%s/commit/%s' % (project, commit)
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        request = urllib2.Request(loginUrl, headers={'PRIVATE-TOKEN':'XYGcYzP8ogCmtS2cuCZo'})
        result = opener.open(request)
        html = result.read().decode('utf-8')
        f = codecs.open("a.html", "w+", "utf-8")
        f.write(html)
        f.close()
         
    def parse_html_backup(self, project, commit):
        f = codecs.open("a.html", "r", "utf-8")
        html = f.read()
        f.close()
        m = re.search(r'<span class="commit-author-name">(\w+)</span>', sectors[0])
        author = m.group(1)
        team = self.accounts_info[author][1]
       #for m in re.finditer(r'<td class="line_content (?:new noteable_line|noteable_line old)" data-discussion-id="[a-f0-9]+" data-line-code="([0-9a-f_]+)" data-line-type="(?:new|old)" data-note-type="DiffNote" data-position="({[^}]+})">(?:(?!data-discussion-id).)*?<tr class="notes_holder">(.*?)</tr>', html, re.DOTALL):
       #for m in re.finditer(r'data-line-code="([0-9a-f_]+)" data-line-type="(?:new|old)" data-note-type="DiffNote" data-position="({[^}]+})"(?:(?!data-discussion-id).)*?<tr class="notes_holder">(.*?)</tr>', html, re.DOTALL):
        for m in re.finditer(r'(<button name="button" type="submit" class="add-diff-note js-add-diff-note-button" data-line-code=).*\1"([0-9a-f_]+)" data-line-type="(?:new|old)" data-note-type="DiffNote" data-position="({[^}]+})".*?<tr class="notes_holder">(.*?)</tr>', html, re.DOTALL):
            note = {}
            note['note'] = self._parse_notes_detail(m.group(4))
            note['ref'] = m.group(2)
            note['fname'] = self._get_fname(m.group(3))
            note['author'] = author
            note['team'] = team
            note['project'] = project
            note['sha1'] = commit
            self.commits_info.append(note)

    def generate_html_report(self):
        content = '''
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
th, td {
    padding: 5px;
    text-align: left;    
}
</style>
</head>
<body>

<h2>All Comments From GitLab:</h2>
<table style="width:100%">
  <tr>
    <th rowspan="1">Project</th>
    <th rowspan="1">Team</th>
    <th rowspan="1">Commit</th>
    <th rowspan="1">Author</th>
    <th rowspan="1">File</th>
    <th colspan="1">Notes</th>
  </tr>
'''

        end = '''
</table>

</body>
</html>    
'''

        for commit_file in self.commits_info:
            note_num = len(commit_file['note'])
            file_info = '''
    <td rowspan="NOTE_NUM">%s</td>         <!--project-->
    <td rowspan="NOTE_NUM">%s</td>      <!--team-->
    <td rowspan="NOTE_NUM">_COMMIT_</td>         <!--commit-->
    <td rowspan="NOTE_NUM">%s</td>         <!--author-->
    <td rowspan="NOTE_NUM">FILE_NAME</td>         <!--file name-->
'''  % (commit_file['project'], commit_file['team'], commit_file['author'])
            #for rowspan
            file_info = file_info.replace('NOTE_NUM', str(note_num))
            
            #for file name
            file_name = '<a href="http://gitlab.china.nsn-net.net/lte/%s/commit/%s#%s">%s:%d</a>' % \
                (commit_file['project'], commit_file['sha1'], commit_file['ref'], commit_file['fname'][0], commit_file['fname'][1])
            file_info = file_info.replace('FILE_NAME', file_name)
            
            #for commit
            commit_text = '<a href="http://gitlab.china.nsn-net.net/lte/%s/commit/%s">%s</a>' % \
                (commit_file['project'], commit_file['sha1'], commit_file['sha1'][0:8])
            file_info = file_info.replace('_COMMIT_', commit_text)

            for note in commit_file['note']:
                note_text = '<b>%s</b> <a href="http://gitlab.china.nsn-net.net/lte/%s/commit/%s#%s">go</a> --by %s' % \
                    (note['note'], commit_file['project'], commit_file['sha1'], note['id'], note['author'])
                content += '''
  <tr>
    %s
    <td>[%s]: %s</td>         <!--date-->
  </tr>
''' % (file_info, note['date'].strftime("%Y-%m-%d"), note_text)
                file_info = ""

        content += end
        f = codecs.open("report.html", "w+", "utf-8")
        f.write(content)
        f.close()

    def _get_total_span_by_project(self, commits):
        count = 0
        for (id, commit) in commits:
            count += self._get_total_span_by_commit(commit)
        return count

    def _get_total_span_by_commit(self, commit):
        count = 0
        for (fname, notes) in commit:
            count += self._get_total_span_by_file(notes)
        return count

    def _get_total_span_by_file(self, notes):
        if len(notes) == 0:
            return 1
        else:
            return len(notes)

if __name__ == "__main__":
    gitlab = Gitlab()

    is_tdd = True
    hash_id = "4b41d2c0af2ad3d66b9528b5dc45771ac244d0fc"
    if is_tdd:
        gitlab.fetch_commit_html("tddps", hash_id)
        gitlab.parse_html("tddps", hash_id)
    else:
        gitlab.fetch_commit_html("fddps", hash_id)
        gitlab.parse_html("fddps", hash_id)
    print gitlab.commits_info
    #gitlab.generate_html_report()
    
