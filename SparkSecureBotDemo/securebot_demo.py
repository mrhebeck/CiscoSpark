"""
Copyright 2016 Cisco Systems Inc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from itty import *
import urllib2
import json

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents
    
def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents
    

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.
    X-Spark-Signature - The header containing the sha1 hash we need to validate
    request.body - the Raw JSON String we need to use to validate the X-Spark-Signature
    """
    raw = request.body
    hashed = hmac.new(key, raw, hashlib.sha1)
    validatedSignature = hashed.hexdigest()
    print 'validatedSignature', validatedSignature
    print 'X-Spark-Signature', request.headers.get('X-Spark-Signature')
    returnVal = ""
    if validatedSignature == request.headers.get('X-Spark-Signature'):
        webhook = json.loads(raw)
        print webhook['data']['id']
        requester = webhook['data']['personEmail']
        if requester != bot_email:
            #get person information, specifically need the person's orgId
            person = sendSparkGET('https://api.ciscospark.com/v1/people/{0}'.format(webhook['data']['personId']))
            if json.loads(person)['orgId'] == my_org_id or requester in auth_users:
                result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
                result = json.loads(result)
                in_message = result.get('text', '').lower()
                in_message = in_message.replace(bot_name, '')
                #echo the message back to the same room
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": in_message})
                returnVal = "success"
            else:
                print "orgId does not match or person not in list of authorized users"
    else:
        print "Secret does not match!"
    return returnVal

####CHANGE THESE VALUES#####
#Replace this with the secret phrase you used in the webhook creation
key = "somesupersecretphrase"
auth_users = ['tahanson@cisco.com'] #change to your email or list of correct email addresses
#Change below line to be your own OrgId
my_org_id = "ORG_ID HERE"
bot_email = "yourbot@sparkbot.io"
bot_name = "yourbot"
bearer = "YOUR TOKEN HERE"
run_itty(server='wsgiref', host='0.0.0.0', port=10010)
