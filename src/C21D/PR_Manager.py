import pycurl
import StringIO
import json
from time import sleep

# Configuration variables
from C21D_Config import *

_files = []

##
# Given a pycurl object, a url of a pending action and its owner
# user, accept the pending action generating a merge with a concrete
# commit title
#
def accept_pr (c,url,usr):
    # Request API to perform and accept the Merge
    c.setopt(c.URL, '%s/merge' % url)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.POSTFIELDS, '{"commit_title" : "Merging from user %s and %s"}' % (usr, url))
    response = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, response.write)

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

##
# Given a pycurl object, a url of a pending action and its owner
# user, reject the pending action
#
def reject_pr(c,url,usr):
    # Request API to close the PR
    c.setopt(c.URL, '%s' % url)
    c.setopt(c.CUSTOMREQUEST, "PATCH")
    c.setopt(c.POSTFIELDS, '{"state" : "close"}')
    response = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, response.write)

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
##
# Given a pycurl object, a url of a pending action and its owner
# user, check the commits of the pending action ensuring that its file
# contents (modification and additions) are the expected ones, in this
# case, files are added into global list
def check_pr(c,url,usr):
    global _files

    # Request API to close the PR
    c.setopt(c.URL, '%s/commits' % url)
    c.setopt(c.CUSTOMREQUEST, "GET")
    c.setopt(c.POSTFIELDS, '')
    response = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, response.write)

    c.perform()

    # Process answer to verify that close has been completed
    ret = response.getvalue()
    response.truncate(0)

    ret_commits = json.loads(ret)

    # Process each Commit in the Pull Request
    for commits in ret_commits:
        c_url = commits["url"]

        c.setopt(c.URL, '%s' % c_url)
        c.perform()

        # Process answer to verify that close has been completed
        ret = response.getvalue()
        response.truncate(0)

        ret_commit = json.loads(ret)

        files = ret_commit['files']
        for f in files:
            print f["filename"],
            print f["status"]
            _files.append (f["filename"])
            # TO-DO : Check file correctness
            # if not: return False

    return True

##
# Ask to the configured repo_baseurl about the pending Pull Request
# and accept them in case of be a correct(and expected)data and from a
# valid user
def process_pr():

    # CURL objects
    c = pycurl.Curl()

    # Retrieve all Pending Pulls Requests from configured github
    # repository
    c.setopt(c.URL, '%s/pulls' % repo_baseurl)
    response = StringIO.StringIO()
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
        url = prs["url"]
        print url

        to_reject = True

        # In case of being a validated user, pending is checked to ensure
        # that contains information only modifiable by the user, in this
        # case pull request is accepted and incorporated into main
        # repository.
        if usr in repo_validated_users:
            if check_pr(c,url,usr):
                #accept_pr (c,url,usr);
                to_reject = False

        # In case of being a invalid user or its contents are not
        # adecuate, pending is closed
        if to_reject:
            reject_pr(c,url,usr);

    # Release Resources
    c.close()
    response.close()


# Main
process_pr()

# Now with repository pull needs to be performed in order to manage
# the files in variable _files
