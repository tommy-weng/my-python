#!/usr/bin/python
from git_save_logs import save_all_logs
from git_log_analyze import AllCommits
from gitlab_get_comments_by_webpage import Gitlab
from mysql_recorder import Recorder


if __name__ == '__main__':
    commits = Recorder("commits")
    all_commits = commits.query("reviewed=1 and reviewedtime < DATE_SUB(NOW(), INTERVAL 1 HOUR) and closed=0")
    for commit in all_commits:
        # check whether it has notes
        


