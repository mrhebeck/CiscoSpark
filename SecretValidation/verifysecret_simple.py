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
import hashlib
import hmac

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.
    X-Spark-Signature - The header containing the sha1 hash we need to validate
    request.body - the Raw JSON String we need to use to validate the X-Spark-Signature
    """
    raw = request.body
    #Let's create the SHA1 signature 
    #based on the request body JSON (raw) and our passphrase (key)
    hashed = hmac.new(key, raw, hashlib.sha1)
    validatedSignature = hashed.hexdigest()
    
    print 'validatedSignature', validatedSignature
    print 'X-Spark-Signature', request.headers.get('X-Spark-Signature')
    print 'Equal?', validatedSignature == request.headers.get('X-Spark-Signature')
    
    return "true"

#Replace this with the secret phrase you used in the webhook creation
key = "somesupersecretphrase"
port = 10007
run_itty(server='wsgiref', host='0.0.0.0', port=port)