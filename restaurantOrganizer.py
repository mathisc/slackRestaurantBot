#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from slackclient import SlackClient
import json
import random
import sys
import argparse



parser = argparse.ArgumentParser(description = 'Restaurant bot!')
parser.add_argument('slackbot_token', type=str, help='An ID for the slackbot')
parser.add_argument('--waiting_time', type=int, default=10, help='Time to let people answer before closing reservations')
parser.add_argument('--group_size', type=int, default=10, help='Maximum group size, if participants > max group size, several groups will be created')
args = parser.parse_args()

MAX_GROUP_SIZE = args.group_size  
WAITING_TIME_MIN =  args.waiting_time

#___ Instantiate Slack client
BOT_NAME = slack_client = SlackClient(args.slackbot_token)
def get_botID():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') =='restaurant-organizer':
                return user.get('id')
    else:
        return None

#___ Constants
BOT_ID = get_botID()
COMMAND_ORGANIZE = "organize"
AT_BOT = "<@" + BOT_ID + "> "
AT_CHAN = "<!channel> "

#___ Functions
def sendReservationMessage(channel):
    response = AT_CHAN
    response += "Up for some crazy restaurant? React to this post during the next " + str(WAITING_TIME_MIN) + " minutes and I'll handle (almost) everything."
    message = slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
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

    slack_client.api_call("chat.postMessage", channel=channel, text=txt, as_user=True)

def organize_command(command, channel):

    messageInit = sendReservationMessage(channel)

    time.sleep(WAITING_TIME_MIN*60)

    reactions = slack_client.api_call("reactions.get",
                                      channel=channel,
                                      timestamp=messageInit['message']['ts'],
                                      as_user=True)

    replies = []
    print(reactions)

    if (len(reactions) == 0):
        return;

    if (len(reactions['message']) == 0):
        return;

    if (len(reactions['message']['reactions']) == 0):
        return;

    for reaction in reactions['message']['reactions'] :
        for user in reaction['users'] :
            replies.append(user)

    #Remove duplicates : if people reacted more than once to the poll
    replies = list(set(replies))
    if (len(replies)==0):
        return

    #Get Actual name
    for i in range(len(replies)):
        userInfo = slack_client.api_call("users.info", user=replies[i], as_user=True)
        replies[i] = userInfo['user']['name']
    print(replies)


    groups = formGroups(replies);
    print(groups)


    sendFinalMessage(channel,groups)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + COMMAND_ORGANIZE + \
               "* command with numbers, delimited by spaces."
    if command.startswith(COMMAND_ORGANIZE):
        organize_command(command,channel)

    print("Done")

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                if AT_BOT in output['text']:
                    return output['text'].split(AT_BOT)[1].strip().lower(), \
                           output['channel']

    return None, None


#___ Main
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("restaurant-organizer connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
