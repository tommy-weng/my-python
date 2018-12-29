#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
#from common.utils import ServerError

def ServerError(msg):
    return RuntimeError(msg)

class GitLabAPI(object):
    def __init__(self, url='', headers=None, *args, **kwargs):
        self.headers = headers
        self.gitlab_url = url

    def get_user_id(self, username):
        user_id = None
        res = requests.get("%s/users?username=%s" % (self.gitlab_url, username), headers=self.headers, verify=True)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        if content:
            user_id = content[0].get('id')
        return user_id

    def get_user_projects(self):
        res = requests.get(self.gitlab_url + "/projects?membership=true", headers=self.headers, verify=True)
        status_code = res.status_code
        print res
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        return content

    def get_user_project_id(self, name):
        """
        :param name: 项目名称 
        :return: 
        """
        project_id = None
        projects = self.get_user_projects()
        if projects:
            for item in projects:
                if item.get('name') == name:
                    project_id = item.get('id')
        return project_id

    def get_project_branchs(self, project_id):
        branchs = []
        res = requests.get("%s/projects/%s/repository/branches"%(self.gitlab_url, project_id), headers=self.headers, verify=True)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        if content:
            for item in content:
                branchs.append(item.get('name'))
        return branchs

    def get_project_tags(self, project_id):
        tags = []
        res = requests.get(self.gitlab_url + "/projects/%s/repository/tags" % project_id,
                           headers=self.headers, verify=False)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        content = res.json()
        if content:
            for item in content:
                tag_name = item.get('name')
                commit = item.get('commit')
                info = ''
                if commit:
                    commit_id = commit.get('id')
                    commit_info = commit.get('message')
                    info = "%s * %s"%(commit_id[:9], commit_info)
                tags.append("%s     %s"%(tag_name, info))
        return tags

    def get_commit_notes(self, project_id, shalId):
        content = []
        url = "%s/projects/%s/repository/commits/%s/comments" % (self.gitlab_url, project_id, shalId)
        res = requests.get(url, headers=self.headers, verify=True)
        status_code = res.status_code
        if status_code != 200:
            raise ServerError(res.get('message'))
        notes = res.json()
        print notes
        if notes:
            for item in notes:
                note = item.get('note')
                content.append(note)
        return content
        
if __name__ == "__main__":
    headers = {'PRIVATE-TOKEN': 'iQHJG7yEtU5psbEEh4Ei'} #你的gitlab账户的private token
    api = GitLabAPI('https://gitlabe1.ext.net.nokia.com/api/v4', headers=headers)
    content = api.get_user_projects()
    user_id = api.get_user_id('sweng1')
    print "user_id:", user_id

    project_id = api.get_user_project_id('tddps')
    print "project:", project_id

    branchs = api.get_project_branchs(project_id)
   # print "project branchs:", branchs

    notes = api.get_commit_notes(project_id, '9a12e541165d7cd8f1d5e4fe38cd4d2ffcb90902')
    print notes
    # tags = api.get_project_tags('345')
    # print "project tags:", tags
