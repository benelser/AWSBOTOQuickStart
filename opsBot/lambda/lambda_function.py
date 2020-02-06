import json
import os
import logging
import urllib.request
import json 
import re

# Bot needs to be created and token generated in slack. 
# Token is used in POST request back to slack private channel
# Bot scope needed: chat:write, im:history
# Subscribe bot to event subscriptions: message.im
BOT_TOKEN = 'xoxb-2697193399-926657851395-Q1e12Kk1KGqiwwNW8PH4daO3'
SLACK_URL = "https://slack.com/api/chat.postMessage"

def myFirstLambda(event, context):
    slack_event = event['event']
    print(slack_event)
    print(slack_event)
    if "challenge" in event:
        return event["challenge"]
    if "bot_id" in slack_event:
        logging.warn("Ignore bot event")
    else:
        # Get the text of the message the user sent to the bot,
        # and reverse it.
        match = re.match(r"\bKill|\bDeploy|\bStart", slack_event["text"]) 
        message = f"""
Please provide one of the following commands:
Deploy:InsightVM
Kill:EC2:(InstanceID)
Start:EC2:(InstanceID)
        """
        if match == None:
            channel_id = slack_event["channel"]
            body = {"channel": channel_id, "text" : message}
            jsondata = json.dumps(body)
            jsondataasbytes = jsondata.encode('utf-8') 
            req = urllib.request.Request(url=SLACK_URL, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {BOT_TOKEN}')
            req.add_header('Content-Length', len(jsondataasbytes))
            response = urllib.request.urlopen(req, jsondataasbytes)
            return "200 OK"
        if match.string.split(":")[0] == 'Kill':
            # TODO: write code...
            ec2  = match.string.split(":")[-1]
            channel_id = slack_event["channel"]
            body = {"channel": channel_id, "text" : f"Killing EC2:{ec2}"}
            jsondata = json.dumps(body)
            jsondataasbytes = jsondata.encode('utf-8') 
            req = urllib.request.Request(url=SLACK_URL, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {BOT_TOKEN}')
            req.add_header('Content-Length', len(jsondataasbytes))
            response = urllib.request.urlopen(req, jsondataasbytes)
            return "200 OK"
        if match.string.split(":")[0] == 'Deploy':
            # TODO: write code...
            ec2  = match.string.split(":")[-1]
            channel_id = slack_event["channel"]
            body = {"channel": channel_id, "text" : f"Deploying InsightVM"}
            jsondata = json.dumps(body)
            jsondataasbytes = jsondata.encode('utf-8') 
            req = urllib.request.Request(url=SLACK_URL, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {BOT_TOKEN}')
            req.add_header('Content-Length', len(jsondataasbytes))
            response = urllib.request.urlopen(req, jsondataasbytes)
            return "200 OK"