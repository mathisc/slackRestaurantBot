#------------------------------------
#- Restaurant bot instructions : ---- 
#------------------------------------

* Installation : 
----------------
This entire bot was designed as described in this tutorial : 
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
(This tutorial also helps you understanding what virtualenv is useful for...)


-> First to use the bot you need to install slackclient (via pip for instance) :
pip install slackclient

-> Then you need to define SLACK_BOT_TOKEN in your environment : 
export SLACK_BOT_TOKEN=value
Its value is not hardcoded due to security reasons but can be found here : 
https://gopro.slack.com/services/B2K6XE1L7 under API TOKEN

* Launch bot deamon : 
-----------------------
From a terminal :
python restaurantorganizer.python

* Invoke bot in slack : 
-----------------------
If the bot is not already present in the targeted channel, add it to the channel.
And then type : 
@restaurant-organizer organize
