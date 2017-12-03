import pycurl
import StringIO
import json
from time import sleep

# Configuration variables
from C21D_Config import *

# CURL objects
response = StringIO.StringIO()
c = pycurl.Curl()

# Retrieve all Pending Pulls Requests from configured github
# repository
c.setopt(c.URL, '%s/pulls' % repo_baseurl)
c.setopt(c.WRITEFUNCTION, response.write)
c.setopt(c.USERPWD, "%s:%s" % (repo_user, repo_pwd))
c.perform()

# Convert response in JSON format into python dictionaries
ret = response.getvalue()
response.truncate(0)
ret_pulls = json.loads(ret)

# Process each Pending Pull Request
for prs in ret_pulls:

    # Ensure that onwer of the PR is in our validated GitHub Users
    # List
    usr = prs["user"]["login"]
    if usr in repo_validated_users:
        # In case of being a valdated user, pending is incorporated
        # into repository
        url = prs["url"]
        print url

        # Request API to perform and accept the Merge
        c.setopt(c.URL, '%s/merge' % url)
        c.setopt(c.CUSTOMREQUEST, "PUT")
        c.setopt(c.POSTFIELDS, '{"commit_title" : "Merging from user %s and %s"}' % (usr, url))

        c.perform()
        sleep(0.5)

        # Process answer to verify that merge has been completed
        ret = response.getvalue()
        response.truncate(0)
        ret_merge = json.loads(ret)
        if 'merged' in ret_merge :
            print "Merged %s" % ret_merge['merged']
        else:
            print "Error while Merging %s: " % url
            print ret

    else:
        # In case of being a invalid user, pending is closed
        url = prs["url"]
        print url

        # Request API to close the PR
        c.setopt(c.URL, '%s' % url)
        c.setopt(c.CUSTOMREQUEST, "PATCH")
        c.setopt(c.POSTFIELDS, '{"state" : "close"}')
        c.perform()

        # Process answer to verify that close has been completed
        ret = response.getvalue()
        response.truncate(0)
        ret_close = json.loads(ret)
        if 'state' in  ret_close:
            print "Closed %s" % ret_close['state']
        else:
            print "error while closing %s :" % url
            print ret

# Release Resources
c.close()
response.close()
