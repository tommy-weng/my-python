#!/usr/bin/python
import os
import subprocess

def save_branch_log(log_name, ref, path, start):
    cur_dir = os.getcwd()
    f = open(log_name, "w")
    os.chdir(os.path.expanduser(path))
    output = subprocess.check_output('git log --numstat --since="%s" --date=iso-local %s' % (start, ref),  shell=True)
    f.write(output)
    os.chdir(cur_dir)
    f.close()

def save_all_logs(start, tracking_info):
    ret = []

    #gitlab.get_all_commits('lte/tddps', 'trunk') 
    for project in tracking_info:
        for branch in tracking_info[project]['branches']:
            print project, branch
            log_name = ("%s-%s.log" % (project, branch)).replace('/', '_')
            ref = "%s/%s" % ( tracking_info[project]['remote'], branch)
            path = tracking_info[project]['path']
            save_branch_log(log_name, ref, path, start)
            ret.append({'project':project, 'branch':branch, 'fname':log_name})
    return ret

if __name__ == "__main__":
    tracking_info = {
        'tddps': {
            'path': '/var/lib/jenkins/workspace/sync-tddps-to-gitlab',
            'remote': 'origin',
            'branches': ['trunk', 'TL16A_MAC_PS_0000_000079_000000_mMIMO']
        },
        'fddps': {
            'path': '/var/lib/jenkins/workspace/sync-fddps-to-gitlab',
            'remote': 'origin',
            'branches': ['trunk', 'maintenance/fb17_07']
        }
    }
    
    save_all_logs("2016-11-27", tracking_info)
