#!/usr/bin/python
from git_save_logs import save_all_logs
from git_log_analyze import AllCommits
#from recorder import Recorder
from mysql_recorder import Recorder

if __name__ == "__main__":
    titles = ['project', 'branch', 'svn', 'sha1', 'author', 'date', 'title', 'fullname', 'team', 'rollbacked']
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
    rec = Recorder("commits")
    all_logs = save_all_logs("2017-12-1", tracking_info)
    for log in all_logs:
        gitlog = AllCommits(log['fname'])
        for commit in gitlog.commits:
            print '{0:40} {1:10} {2:19}'.format(commit.info['sha1'], commit.info['author'], str(commit.info['date']))
            if commit.info['sha1'] == '28f2b683290a7b08011eb58d4533720e0461e0d5':
              continue
            line = {}
            for i in range(0, len(titles)):
                e = titles[i]
                if e == 'project':
                    line[e] = log['project']
                elif e == 'branch':
                    line[e] = log['branch']
                elif e == 'svn' or e == 'rollbacked':
                    pass
                #elif e == 'date':
                #    line[e] = commit.info[e].strftime('%Y-%m-%d %H:%M:%S')
                elif e == 'title':
                    if len(commit.info['feature']) > 0:
                        line[e] = commit.info['feature'] + ':' + commit.info[e]
                    else:
                        line[e] = commit.info[e]
                else:
                    line[e] = commit.info[e]
            rec.update(line, "sha1")
