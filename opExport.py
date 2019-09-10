#!/usr/bin/env python

# Export all messages from Ontraport to HTML

import os.path
import json
import argparse
import urllib2

API_BASE_URL = 'https://api.ontraport.com/1/'
CURDIR = os.path.dirname(os.path.realpath(__file__))
OUTDIR = os.path.join(CURDIR, 'opMessages')
MSGMAX = 600

# start value; increment this 
msgStart = 0
# messages to get per loop execution
msgCount = 30

# collect Message objects here. Derp.
messages = []

class Message(object):
    def __init__(self, mid, subj, body):
        self.id = mid
        self.subj = subj
        self.body = body

def buildParser():
    """Build and return argument parser"""
    p = argparser.ArgumentParser()
    p.add_argument('--key', dest='apikey')
    p.add_argument('--appid', dest='appid')
    return p

def buildMessageObjectList(appid, apikey, msgStart, msgCount):
    # https://api.ontraport.com/1/Messages?start=1&range=50&sort=id&sortDir=asc&listFields=id%2Csubject%2Cmessage_body
    u = API_BASE_URL + 'Messages?'
    u += 'start='+str(msgStart)
    u += '&range='+str(msgCount)
    u += '&sort=id&sortDir=desc&listFields=id%2Csubject%2C%message_body'
    
    req = urllib2.Request(u)
    req.add_header('Api-Appid': appid)
    req.add_header('Api-Key': apikey)

    try:
        response = urllib2.urlopen(req)
    except Exception, e:
        print "Something pooped the bed:"
        print type(e)
        print e

    # this should be JSON data
    payload = response.read()

    print payload 

def dumpMessageAsHtml(messageObject):
    """Write the message body to a file"""
    pass

p = buildParser()
p.parse_args()

