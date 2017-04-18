#!/usr/bin/env python
# -*- coding: utf-8 -*-

from slackclient import SlackClient

def get_botID(slack_client, name):
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == name:
                return user.get('id')
    else:
        return None


#___ Slack Constants
def get_slackConstants(slackbot_token, name):
    SLACK_CLIENT = SlackClient(slackbot_token)
    BOT_ID = get_botID(SLACK_CLIENT, name)
    AT_BOT = "<@" + BOT_ID + "> "
    AT_CHAN = "<!channel> "
    return  SLACK_CLIENT,BOT_ID,AT_BOT,AT_CHAN

#___ Functions
def parse_slack_output(slack_rtm_output, AT_BOT):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                if AT_BOT in output['text']:
                    return output['text'].split(AT_BOT)[1].strip().lower(), \
                           output['channel']

    return None, None
