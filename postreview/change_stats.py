#!/usr/bin/python
from git_save_logs import save_all_logs
from git_log_analyze import AllCommits
from recorder import Recorder

if __name__ == "__main__":
    titles = ['new', 'svn', 'change-id', 'author', 'date', 'type', 'feature', 'title', 'file', 
        'add', 'del', 'ftype', 'fb', 'fullname', 'team', 'branch']
    tracking_info = {
        'tddps': {
            'path': '/home/qrb378/trunk_git',
            'remote': 'mirror',
            'branches': ['trunk', 'TL16A_MAC_PS_0000_000079_000000_mMIMO']
        },
        'fddps': {
            'path': '/home/qrb378/fddps',
            'remote': 'origin',
            'branches': ['trunk', 'maintenance/fb17_07']
        }
    }
    
    rec = Recorder("commit-report.xlsx")
    rec.write(titles)
    all_logs = save_all_logs("2016-10-1", tracking_info)
    for log in all_logs:
        gitlog = AllCommits(log['fname'])
        for commit in gitlog.commits:
            print commit.info['commit'], commit.info['author'], commit.info['date']
            line = []
            for i in range(0, len(titles)):
                e = titles[i]
                if e == 'new':
                    line.append(1)
                elif e in ['file', 'add', 'del', 'ftype']:
                    line.append('')
                else:
                    line.append(commit.info[e])
            for change in commit.info['changes']:
                line[8] = change['file']
                line[9] = change['add']
                line[10] = change['del']
                line[11] = change['ftype']
                rec.write(line)
                line[0] = 0
    rec.close()
