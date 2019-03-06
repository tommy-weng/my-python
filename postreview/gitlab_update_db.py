#!/usr/bin/python
from git_save_logs import save_all_logs
from git_log_analyze import AllCommits
from pymongo import MongoClient

def save_to_db(commits):
    client = MongoClient('10.56.78.54', 8999)
    db = client['gitlab']
    collection = db['commits']
    for commit in commits:
        if collection.find({"commit": commit.info['commit']}).count() == 0:
            print "Insert %s to db" % (commit.info['commit'])
            collection.insert_one(commit.info)

if __name__ == '__main__':
    #save_all_logs()
    all_logs = {'tddps-trunk.log':'tddps', 'tddps-TL16A_MAC_PS_0000_000079_000000_mMIMO.log':'tddps', 'fddps-trunk.log':'fddps'}
    for (log, project) in all_logs.iteritems():
        gitlog = AllCommits(log)
        save_to_db(gitlog.commits)
