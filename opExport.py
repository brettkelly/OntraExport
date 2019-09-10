#!/usr/bin/env python

# Copyright 2019 Brett Kelly
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.

# Export all messages from Ontraport to HTML. This is for Python 2.7, in 
# case you wanted to break out your fancy Python 3.x.

##
# Here's what this thing does:
# 1. Connects to the Ontraport API
# 2. Downloads and saves messages (total based on the --max parameter)
# 3. Writes each message to an HTML file where the name is:
#   [ID]-[Subject].html
# 4. That's it. No formatting, no mucking with the markup, no funny stuff.
#
# Contains minimal error checking; Doesn't respect rate limits or even
# check to see if they exist. This is a one-off pile of crap I wrote to save
# myself from downloading hundreds of messages. Good thing I'm not a 
# real programmer.
# 
# Also, Ontraport needs a UI for exporting messages.
# 
# Run with the -h parameter for usage.
##

import os.path
import json
import argparse
import urllib2

API_BASE_URL = 'https://api.ontraport.com/1/'
CURDIR = os.path.dirname(os.path.realpath(__file__))
OUTDIR = os.path.join(CURDIR, 'exported')

# start value; increment this 
msgStart = 0
# messages to get per loop execution
msgCount = 30

# collect Message objects here. Derp.
messages = []
# collect ids of messages that break
badMsgs = []

class Message(object):
    "Value object, blah blah blah"
    def __init__(self, mid, subj, body):
        self.id = mid
        self.subj = subj
        self.body = body

def buildParser():
    "Build and return argument parser"
    p = argparse.ArgumentParser()
    p.add_argument('--key', dest='apikey' ,required=True)
    p.add_argument('--appid', dest='appid', required=True)
    p.add_argument('--max', dest='maxcount', 
            help='Total number of messages to retrieve', default=600)
    p.add_argument('--verbose', action='store_true', 
            default=False, help='Add lots of output you probably don\'t want')
    return p

def retrieveMessageObjects(appid, apikey, msgStart, msgCount, verbose):
    "Connect to the Ontraport API and download [msgCount] messages"
    u = API_BASE_URL + 'Messages?'
    u += 'start='+str(msgStart)
    u += '&range='+str(msgCount)
    # Grab ID, Subject, and Message Body. Sort by ID.
    u += '&sort=id&sortDir=desc&listFields=id%2Csubject%2Cmessage_body'

    if verbose:
        print "Next request URL:"
        print u
    
    req = urllib2.Request(u)
    req.add_header('Api-Appid', appid)
    req.add_header('Api-Key', apikey)

    try:
        response = urllib2.urlopen(req)
    except Exception, e:
        print "Something pooped the bed:"
        print type(e)
        print e

    dataDict = json.load(response)
    for msg in dataDict['data']:
        try:
            mid = msg['id']
            if verbose:
                print "Processing Message: %s" % mid
            subj = msg['subject']
            body = msg['message_body'].encode('utf-8')
            m = Message(mid, subj, body)
            messages.append(m)
        except Exception, e:
            if verbose:
                print type(e)
                print "Error with message %s" % mid
            badMsgs.append(mid)

def dumpMessageAsHtml(messageObject):
    """Write the message body to a file"""
    fname = "%s.html" % str(messageObject.id)
    with open(os.path.join(OUTDIR, fname), 'w') as fd:
        fd.write(messageObject.body)

# Check for the output directory; quit if it's missing
# This should create it, but whatever. I don't care.
if not os.path.exists(OUTDIR):
    print "Output directory doesn't exist, turkey:"
    print OUTDIR
    print "Create this directory and try again."
    raise SystemExit

p = buildParser()
args = p.parse_args()
verbose = bool(vars(args)['verbose'])

# Get message objects in batches of msgCount
while msgStart < int(vars(args)['maxcount']):
    retrieveMessageObjects(vars(args)['appid'], \
            vars(args)['apikey'],  msgStart, msgCount,  verbose)
    msgStart += msgCount

# write the output files
for message in messages:
    dumpMessageAsHtml(message)

# Deliver the news
print "Total messages written: %d" % len(messages)
print "Total errors: %d" % len(badMsgs)
