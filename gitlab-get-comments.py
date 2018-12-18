import json
import urllib2
import requests

#curl --header "PRIVATE-TOKEN: XYGcYzP8ogCmtS2cuCZo" "http://gitlabe1.ext.net.nokia.com/api/v4/projects/19631/repository/commits/c97bda7a55559b0bc99fb31b9b7bfc450e0f0bf2/comments";
'''
login_url = 'http://gitlabe1.ext.net.nokia.com/api/v4/projects/19631/repository/commits/c97bda7a55559b0bc99fb31b9b7bfc450e0f0bf2/comments'
request = urllib2.Request(login_url, headers={'PRIVATE-TOKEN':'XYGcYzP8ogCmtS2cuCZo'})

response = urllib2.urlopen(request) 
the_page = response.read()
print the_page
'''

github_url = 'http://gitlabe1.ext.net.nokia.com/api/v4/projects/19631/repository/commits/c97bda7a55559b0bc99fb31b9b7bfc450e0f0bf2/comments'
r = requests.post(github_url, headers={'PRIVATE-TOKEN':'XYGcYzP8ogCmtS2cuCZo'}) 
print r.json 