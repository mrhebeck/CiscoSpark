/*
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
*/

// External libraries
var request = require('request');
var http = require('http');
var irc = require('irc');

// Predefined variables

var portNumber = 8080; // Set listen port number
var botName = {irc:'IRCToSparkBot', spark:'IRCToSparkBot', sparkEmail:'IRCToSparkBot@sparkbot.io'}; // The name of your bot
var myChannel = '#mychan'; // The channel your bot is active on
var myToken = ''; // user/bot bearer token
var myRoomID = ''; // Spark RoomId for bot
var sparkHeaders = {'content-type': 'application/json; charset=utf-8', 'Authorization':'Bearer ' + myToken}; // Basic Cisco Spark Header
var messagesURL = 'https://api.ciscospark.com/v1/messages/'; // Spark Messages API URL, do not modify
var helpMessage = 'This is an example help message for the IRC to Spark bot.';
var commands = {
  m:{args:0},
  pm:{args:1},
  help:{args:0}
};

function messageInterpreter(myMessage) {

  var myReturnObj = {};
  var preProcessedString = myMessage;
  var index = 0;
  
  if (myMessage === undefined) {
    return '';
  }
  
  //Determines Command
  preProcessedString = myMessage.slice(myMessage.search(botName.spark) + botName.spark.length + 1);
  if (preProcessedString.includes(' ')) {
    index = preProcessedString.search(' ');
    myReturnObj.command = preProcessedString.slice(0, index);
    preProcessedString = preProcessedString.slice(index + 1);
  } else {
    myReturnObj.command = preProcessedString.slice(0);
    return myReturnObj;
  }

  if (commands.hasOwnProperty(myReturnObj.command)) {
    myReturnObj.argument = {};
    for (i = 0; i < commands[myReturnObj.command].args; i++) {
      index = preProcessedString.search(' ');
      myReturnObj.argument[i] = preProcessedString.slice(0, index);
      preProcessedString = preProcessedString.slice(index + 1);
    }
    myReturnObj.value = preProcessedString;
  }
  return myReturnObj;
}

function sendRequest(myURL, myMethod, myHeaders, myData, callback) { // Sends RESTful requests
  
  var options = {
    url: myURL,
    method: myMethod,
    json: true,
    headers: myHeaders,
    body: myData
  };
  
  var res = '';
  
  request(options, function optionalCallback(error, response, body) {
    if (error) {
      res = "Request Failed: " + error;
    } else {
      res = body;
    }
    callback(res)
  });
}

var bot = new irc.Client('irc.freenode.net', botName.irc, { //Connect to IRC
    channels: [myChannel]
});

bot.addListener('message' + myChannel, function (from, message) { // Add listener for channel
  sendRequest(messagesURL, "POST", sparkHeaders, { roomId: myRoomID, text: from + ': ' + message}, function(resp){});
});

bot.addListener('pm', function (from, message) { // Add listener for PM
  sendRequest(messagesURL, "POST", sparkHeaders, { roomId: myRoomID, text: 'PM from ' + from + ': ' + message}, function(resp){});
});

bot.addListener('join', function(channel, who) { // Add listener for user joins
  sendRequest(messagesURL, "POST", sparkHeaders, { roomId: myRoomID, text: who + ' has joined ' + channel + ' - '}, function(resp){});
});

bot.addListener('part', function(channel, who, reason) { // Add listener for user parts
  sendRequest(messagesURL, "POST", sparkHeaders, { roomId: myRoomID, text: who + ' has left ' + channel + ' - '}, function(resp){});
});


http.createServer(function (req, res) { // Set up web listener to receive Webhook POST / Relaying. AKA the magic.
  if (req.method == 'POST') {

    req.on('data', function(chunk) {
      var resObj = JSON.parse(chunk.toString());
      sendRequest(messagesURL + resObj.data.id, "GET", sparkHeaders, '', function(resp){
        var myMessageObj = {};
        if (resp.personEmail != botName.sparkEmail) {myMessageObj = messageInterpreter(resp.text);}
        
        switch (myMessageObj.command) {
          case 'pm': 
            if (bot.chans[myChannel].users.hasOwnProperty(myMessageObj.argument[0]) && myMessageObj.value !== '') {
              bot.say(myMessageObj.argument[0], myMessageObj.value);
            } else if (myMessageObj.value === '') {
              sendRequest(messagesURL, "POST", sparkHeaders, { roomId: myRoomID, text: 'PM FAILED TO ' + myMessageObj.argument[0] + ' FAILED: NO VALUE TO SEND'}, function(resp){});
            } else {
              sendRequest(messagesURL, "POST", sparkHeaders, { roomId: myRoomID, text: 'PM FAILED: USER ' + myMessageObj.argument[0] + ' DOESNT EXIST '}, function(resp){});
            }
            break;
            
          case 'm':
            bot.say(myChannel, myMessageObj.value);
            break;
            
          case 'help':
            sendRequest(messagesURL, "POST", sparkHeaders, { roomId: myRoomID, text: helpMessage}, function(resp){});
            break;
            
        }
      });
    });

    req.on('end', function() {
      res.writeHead(200, "OK", {'Content-Type': 'text/html'});
      res.end();
    });

  } else {
    console.log("[405] " + req.method + " to " + req.url);
    res.writeHead(405, "Method not supported", {'Content-Type': 'text/html'});
    res.end('405 - Method not supported');
  }
}).listen(portNumber); // listen on tcp portNumber value (all interfaces)
