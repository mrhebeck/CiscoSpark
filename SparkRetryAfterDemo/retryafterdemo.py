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

import urllib2
import json
import time

def sendSparkGET(url):
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    response = urllib2.urlopen(request)
    return response

bearer = "BEARER_TOKEN_HERE"

while True:
    try:
        result = sendSparkGET('https://api.ciscospark.com/v1/rooms')
        print result.code, time.time(), result.headers['Trackingid']
    except urllib2.HTTPError as e:
        if e.code == 429:
            print 'code', e.code
            print 'headers', e.headers
            print 'Sleeping for', e.headers['Retry-After'], 'seconds'
            sleep_time = int(e.headers['Retry-After'])
            while sleep_time > 10:
                time.sleep(10)
                sleep_time -= 10
                print 'Asleep for', sleep_time, 'more seconds'
            time.sleep(sleep_time)
        else:
            print e, e.code
            break