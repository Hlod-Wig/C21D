import pycurl
import StringIO
import json
from time import sleep
import base64

# Configuration variables
from C21D_Config import *

##
# Given a file upload it into a personal branch
#
def process(path, filename):

    f = open(filename, "r")

    if f == None:
        print "File %s not found" % filename
        return

    text = f.read()
    f.close()

    # CURL objects
    c = pycurl.Curl()

    c.setopt(c.URL, '%s/git/refs/heads/%s' % (repo_baseurl, repo_user_app))
    response = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, response.write)
    c.setopt(c.USERPWD, "%s:%s" % (repo_user, repo_pwd))
    c.perform()

    # Convert response in JSON format into python dictionaries
    ret = response.getvalue()
    response.truncate(0)
    ret_dict = json.loads(ret)

    sha = ""
    if 'url' not in  ret_dict:
        print "Branch not found, creating"
        c.setopt(c.URL, '%s/git/refs/heads/master' % (repo_baseurl))
        c.perform()
        # Convert response in JSON format into python dictionaries
        ret = response.getvalue()
        response.truncate(0)
        ret_dict = json.loads(ret)
        sha = ret_dict['object']['sha']

        c.setopt(c.URL, '%s/git/refs' % (repo_baseurl))
        c.setopt(c.CUSTOMREQUEST, "POST")
        c.setopt(c.POSTFIELDS, '{"ref" : "refs/heads/%s", "sha" : "%s"}' % (repo_user_app, sha))
        c.perform()

        # Convert response in JSON format into python dictionaries
        ret = response.getvalue()
        response.truncate(0)
        print ret
    else:
        sha = ret_dict['object']['sha']

    c.setopt(c.URL, '%s/git/commits/%s' % (repo_baseurl, sha))
    c.setopt(c.CUSTOMREQUEST, "GET")
    c.setopt(c.POSTFIELDS, '')
    c.perform()
    # Convert response in JSON format into python dictionaries
    ret = response.getvalue()
    response.truncate(0)
    ret_dict = json.loads(ret)
    tree_sha = ret_dict['tree']['sha']
    print ret
    print tree_sha

    c.setopt(c.URL, '%s/git/blobs' % (repo_baseurl))
    c.setopt(c.CUSTOMREQUEST, "POST")
    c.setopt(c.POSTFIELDS, '{"content" : "%s", "encoding" : "base64"}' % base64.b64encode(text))
    c.perform()

    # Convert response in JSON format into python dictionaries
    ret = response.getvalue()
    response.truncate(0)
    ret_dict = json.loads(ret)
    print ret
    blob_sha = ret_dict['sha']

    c.setopt(c.URL, '%s/git/trees' % (repo_baseurl))
    c.setopt(c.CUSTOMREQUEST, "POST")
    c.setopt(c.POSTFIELDS, '{"base_tree": "%s","tree": [{"path": "%s/%s", "mode": "100644", "type": "blob", "sha": "%s"}]}' % (tree_sha, path, filename, blob_sha))
    c.perform()

    # Convert response in JSON format into python dictionaries
    ret = response.getvalue()
    print ret
    response.truncate(0)
    ret_dict = json.loads(ret)
    newtree_sha = ret_dict['sha']

    c.setopt(c.URL, '%s/git/commits' % (repo_baseurl))
    c.setopt(c.CUSTOMREQUEST, "POST")
    c.setopt(c.POSTFIELDS, '{"parents": ["%s"], "tree": "%s", "message": "Update the file"}' % (sha, newtree_sha))
    c.perform()

    # Convert response in JSON format into python dictionaries
    ret = response.getvalue()
    response.truncate(0)
    ret_dict = json.loads(ret)
    print ret
    newcommit_sha = ret_dict['sha']

    c.setopt(c.URL, '%s/git/refs/heads/%s' % (repo_baseurl, repo_user_app))
    c.setopt(c.CUSTOMREQUEST, "POST")
    c.setopt(c.POSTFIELDS, '{"ref": "refs/heads/%s", "sha": "%s"}' % (repo_user_app, newcommit_sha))
    c.perform()

    # Convert response in JSON format into python dictionaries
    ret = response.getvalue()
    response.truncate(0)
    ret_dict = json.loads(ret)
    print ret

    # Release Resources
    c.close()
    response.close()

##
# Merge Personal Branch into Master
#
def merge():

    # CURL objects
    c = pycurl.Curl()

    c.setopt(c.URL, '%s/merges' % repo_baseurl)
    response = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, response.write)
    c.setopt(c.USERPWD, "%s:%s" % (repo_user, repo_pwd))
    c.setopt(c.CUSTOMREQUEST, "POST")
    c.setopt(c.POSTFIELDS, '{"base" : "master", "head" : "%s", "commit_message": "merged"}' % (repo_user_app))
    c.perform()

    # Convert response in JSON format into python dictionaries
    ret = response.getvalue()
    response.truncate(0)
    # ret_dict = json.loads(ret)
    print ret
    # Release Resources
    c.close()
    response.close()

def usage():
    print
    print "Usage: Uploader.py user [path on gitgub] [merge|file]"
    print
    print "To upload a text file under personal branch (creating the branch if is needed) or merge the branch into main"

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 3:
        repo_user_app = sys.argv[1]
        filename = sys.argv[2]
        if m == "merge":
            merge()
        else:
            process(file)
    elif len(sys.argv) == 4:
        repo_user_app = sys.argv[1]
        path = sys.argv[2]
        filename = sys.argv[3]
        process(path, filename)
    else:
        usage()
        sys.exit(0)
