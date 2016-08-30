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
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request)
    return contents


@post('/')
def index(request):
    webhook = json.loads(request.body)
    if webhook['data'].has_key('files'):
        for file_url in webhook['data']['files']:
            response = sendSparkGET(file_url)
            content_disp = response.headers.get('Content-Disposition', None)
            if content_disp is not None:
                filename = content_disp.split("filename=")[1]#split on the string "filename=", then save the second item as name
                filename = filename.replace('"', '')
                with open(filename, 'w') as f:
                    f.write(response.read())
                    print 'Saved-', filename
            else:
                print "Cannot save file- no Content-Disposition header received."
    else:
        print "No files attached to retrieve!"
    return "true"


####CHANGE THIS VALUE#####
bearer = "BOT_TOKEN_HERE"

run_itty(server='wsgiref', host='0.0.0.0', port=10002)