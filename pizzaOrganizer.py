#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from commonTools import *
import os
import time
from slackclient import SlackClient
import json
import random
import sys

parser = argparse.ArgumentParser(description = 'Pizza bot!')
parser.add_argument('slackbot_token', type=str, help='An ID for the slackbot')
parser.add_argument('--waiting_time', type=int, default=10, help='Time to let people answer before closing reservations')
args = parser.parse_args()

SLACKBOT_TOKEN = args.slackbot_token
WAITING_TIME_MIN =  args.waiting_time
COMMAND_WORD = "organize"
SLACK_CLIENT ,BOT_ID ,AT_BOT, AT_CHAN = get_slackConstants(SLACKBOT_TOKEN, "pizza-organizer")

#___ Functions
def parseChoices():
    choices = [ ]
    inputFile = "pizzaChoices.txt"
    f = open(inputFile,'r')
    lines = f.readlines()
    f.close()
    for i in range(len(lines)/4):
        name = lines[4*i].rstrip('\r\n')
        ingredients = lines[4*i + 1].rstrip('\r\n')
        price =lines[4*i + 2].rstrip('\r\n')
        #One empty line to skip to next pizza
        choices.append((name,ingredients,price))
    return choices

def sendReservationMessage(channel,choices):
    response = AT_CHAN
    response += "Up for some pizza? :pizza_pie: React to the pizza you'd like during the next " + str(WAITING_TIME_MIN) + " minutes and I'll handle (almost) everything."
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    messages = []
    for i in range(len(choices)):
        choice = ":pizza: *" + choices[i][0] + " (" + choices[i][2] + ") " + "*" + " \n"
        choice +=  "_" + choices[i][1] + "_"
        message = SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=choice, as_user=True)
        messages.append(message)
    return messages

def sendFinalMessage(channel, choices, replies):
    response = AT_CHAN
    response += "Here is the list of pizza choices : \n"
    for i in range(len(choices)):
        if (len(replies[i]) == 0):
            continue
        response += "-> " + str(len(replies[i])) + " " + choices[i][0] + " for "
        noDuplicates =list(set(replies[i]))
        for u in range(len(noDuplicates)):
             response += noDuplicates[u] + " "
        response += " \n"

    response += "*" + pickReservationResponsible(replies) + "*" + " is responsible for booking the pizzas and bringing them back safely to the office! Here is the phone number : 09 81 97 35 51"
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def pickReservationResponsible(replies):
    candidates = []
    for i in range(len(replies)):
        if (len(replies[i]) == 0):
            continue
        for u in range(len(replies[i])):
            candidates.append(replies[i][u])

    return candidates[random.randint(0, len(candidates) - 1)]

def pizzaCommand(channel):
    choices = parseChoices()
    messageInit = sendReservationMessage(channel, choices)
    time.sleep(WAITING_TIME_MIN*60)
    replies = []
    for i in range(len(messageInit)):
        reactions = SLACK_CLIENT.api_call("reactions.get",
                                      channel=channel,
                                      timestamp=messageInit[i]['message']['ts'],
                                      as_user=True)
        t = []
        if (('message' in reactions) and ('reactions' in reactions['message'])):
            for reaction in reactions['message']['reactions'] :
                for user in reaction['users'] :
                    userInfo = SLACK_CLIENT.api_call("users.info", user=user, as_user=True)
                    t.append(userInfo['user']['name'])

        replies.append(t)

    sendFinalMessage(channel,choices,replies)


#___ Main
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if SLACK_CLIENT.rtm_connect():
        print("pizza-organizer connected and running!")
        while True:
            command, channel = parse_slack_output(SLACK_CLIENT.rtm_read(),AT_BOT)
            if command and channel:
                if command.startswith(COMMAND_WORD):
                    pizzaCommand(channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


