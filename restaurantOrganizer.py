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

parser = argparse.ArgumentParser(description = 'Restaurant bot!')
parser.add_argument('slackbot_token', type=str, help='An ID for the slackbot')
parser.add_argument('--waiting_time', type=int, default=10, help='Time to let people answer before closing reservations')
parser.add_argument('--group_size', type=int, default=10, help='Maximum group size, if participants > max group size, several groups will be created')
args = parser.parse_args()

SLACKBOT_TOKEN = args.slackbot_token
MAX_GROUP_SIZE = args.group_size  
WAITING_TIME_MIN =  args.waiting_time
COMMAND_WORD = "organize"
SLACK_CLIENT ,BOT_ID ,AT_BOT, AT_CHAN = get_slackConstants(SLACKBOT_TOKEN, "restaurant-organizer")


#___ Functions
def sendReservationMessage(channel):
    response = AT_CHAN
    response += "Up for some crazy restaurant? React to this post during the next " + str(WAITING_TIME_MIN) + " minutes and I'll handle (almost) everything."
    message = SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    return message

def formGroups(replies):
    nBins = (len(replies) / MAX_GROUP_SIZE) + 1
    sizeBinsMin = len(replies)/nBins
    groups = [[] for i in xrange(nBins)]

    for bin in range(nBins-1) :
        for i in range(sizeBinsMin):
            userPicked = replies[random.randint(0, len(replies) - 1)]
            groups[bin].append(userPicked)
            replies.remove(userPicked)

    groups[nBins-1] = replies

    return groups

def pickGroupResponsible(group):
    return group[random.randint(0, len(group) - 1)]

def sendFinalMessage(channel, groups):

    txt = AT_CHAN
    txt += "Reservation are now closed !!! \n"
    if (len(groups) > 1) :
        txt += "In order to provide the best available restaurant experience " + str(len(groups)) + " groups have been randomly created \n"

    for i in range(len(groups)):
        txt += "Groups #" + str(i+1) + " with " + str(len(groups[i]))+ " persons : \n"
        for k in range(len(groups[i])):
            txt += groups[i][k] + " \n"
        txt += "<@" + pickGroupResponsible(groups[i]) + "> is in charge of booking the restaurant! \n"
        txt += random.choice(["May the Force be with you.", "Everybody's counting on you!", "HaHaHa screw you!", "Everybody's counting on you!", "I hope we are going to McDonald's", "Don't forget @restaurant-organizer, I'm hungry too!"])

    SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=txt, as_user=True)

def restaurantCommand(channel):

    messageInit = sendReservationMessage(channel)

    time.sleep(WAITING_TIME_MIN*60)

    reactions = SLACK_CLIENT.api_call("reactions.get",
                                      channel=channel,
                                      timestamp=messageInit['message']['ts'],
                                      as_user=True)

    replies = []

    if (not('message' in reactions) or not('reactions' in reactions['message'])):
        return

    for reaction in reactions['message']['reactions'] :
        for user in reaction['users'] :
            replies.append(user)

    #Remove duplicates : if people reacted more than once to the poll
    replies = list(set(replies))
    if (len(replies)==0):
        return

    #Get Actual name
    for i in range(len(replies)):
        userInfo = SLACK_CLIENT.api_call("users.info", user=replies[i], as_user=True)
        replies[i] = userInfo['user']['name']
    print(replies)


    groups = formGroups(replies);
    print(groups)


    sendFinalMessage(channel,groups)

#___ Main
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if SLACK_CLIENT.rtm_connect():
        print("restaurant-organizer connected and running!")
        while True:
            command, channel = parse_slack_output(SLACK_CLIENT.rtm_read(), AT_BOT)
            if command and channel:
                if command.startswith(COMMAND_WORD):
                    restaurantCommand(channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
