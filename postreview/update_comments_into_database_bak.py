#!/usr/bin/python
from git_save_logs import save_all_logs
from git_log_analyze import AllCommits
from gitlab_get_comments_by_webpage import Gitlab
from mysql_recorder import Recorder
import re

def need_update(sha1, comment_db, note_db):
    comments = comment_db.query("sha1='%s'" % sha1)
    if 0 == len(comments):
        return True
    for comment in comments:
        notes = note_db.query("ref='%s'" % comment[0])
        need = True
        for note in notes:
            if None != re.search(r'[Dd]one|[Rr]eject', note[3]):
                need = False
                break
        if need:
            return True
    return False

def parse_gitlab(all_logs, comments, notes_db):
    gitlab = Gitlab()
    for log in all_logs:
        gitlog = AllCommits(log['fname'])
        project = log['project']
        for commit in gitlog.commits:
            if not need_update(commit.info['sha1'], comments, notes_db):
                continue
            print "%s %10s %s" % (commit.info['sha1'], commit.info['author'], commit.info['date'])
            gitlab.fetch_commit_html(project, commit.info['sha1'])
            gitlab.parse_html(project, commit.info['sha1'])

    for info in gitlab.commits_info:
        notes = info["note"]
        del info["note"]
        info["ref"] = info["sha1"] + "#" + info["ref"]
        info["fname"] = "%s:%d" % (info["fname"][0], info["fname"][1])
        comments.update(info, "ref")
        for n in notes:
            n["ref"] = info["ref"]
            notes_db.update(n, "id")

if __name__ == '__main__':
    tracking_info = {
        'tddps': {
            'path': '/var/lib/jenkins/workspace/sync-tddps-to-gitlab',
            'remote': 'origin',
            'branches': ['trunk', 'TL16A_MAC_PS_0000_000079_000000_mMIMO', 'TL18', 'TL18A']
        },
        'fddps': {
            'path': '/var/lib/jenkins/workspace/sync-fddps-to-gitlab',
            'remote': 'origin',
            'branches': ['trunk', 'maintenance/fb17_07', 'maintenance/fb17_12', 'maintenance/fb17_03_SBTS17A']
        }
    }
    
    #all_logs = save_all_logs("2016-11-27", tracking_info)
    all_logs = save_all_logs("2019-1-10", tracking_info)
    
    comments = Recorder("comments")
    notes_db = Recorder("notes")

    print need_update("54cbf9648dd2bc5b945491a740325d73659f6c78", comments, notes_db)
    #parse_gitlab(all_logs, comments, notes_db)

