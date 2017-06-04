from __future__ import print_function
from itty import *
import urllib2, urllib
import json

import httplib2
import os
import json

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
#SCOPES = 'https://www.googleapis.com/auth/drive'

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.
        
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        
        Returns:
        Credentials, the obtained credential.
        """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def sendSparkGET(url):
    """
        This method is used for:
        -Retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
        """
    request = urllib2.Request(url,
                              headers={"Accept" : "application/json",
                              "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents


@post('/')
def index(request):
    """
        When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark, using the sendSparkGET() function.  The message text is parsed.
        """
    
    webhook = json.loads(request.body)
    #print webhook['data']['id']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        print (in_message)
        main(in_message)
        send_tropo(in_message)
        return "true"



####CHANGE THESE VALUES#####
bot_email = "Your Bot Username"
bot_name = "Your Bot Display Name"
bearer = "Your Bot Bearer Token"


def main(in_message):
    """
        This method is used for:
        -Retrieving message text, when the webhook is triggered with a message
        -Then post the message to a blank Google Spreadsheet to notify a user there came a Spark message from his bot.
        -Creates a Sheets API service object:
        https://docs.google.com/spreadsheets/d/1ZDu8T6x77KUSh-Hq4fzW9NCgTx0EU_rWI7lWuPCOEjc/edit
        """
    print("Message sent to bot: {0}".format(in_message))
    #The above print function is used to verify whether the retrieved message content is correct via terminal.
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
discoveryServiceUrl=discoveryUrl)
                    
    spreadsheetId = 'Your Google spreadsheetId'
    rangeName = 'A1'
    body = {"values":[[in_message]]}
    result = service.spreadsheets().values().append(
spreadsheetId=spreadsheetId, range=rangeName, valueInputOption = 'RAW', insertDataOption = 'INSERT_ROWS', body = body).execute()
    return 'ok'

def send_tropo(spark_msg):
    """
       This method is used for:
       -Sending the retrieved message to some one's cell phone via a Tropo SMS application just to notify a Spark message from his Bot was received in the Google Spreadsheet.
       """
    url = 'https://api.tropo.com/1.0/sessions'
    headers = {'accept':'application/json','content-type':'application/json'}
    values = {'token':'MESSAGING TOKEN FROM TROPO APP', 'msg': spark_msg }
    data = json.dumps(values)
    req = urllib2.Request(url = url , data = data, headers = headers)
    response = urllib2.urlopen(req)
    return 'ok'

run_itty(server='wsgiref', host='0.0.0.0', port=10080)

