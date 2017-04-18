* Installation : 
----------------
This entire bot was designed as described in this tutorial : 
** restaurantOrganizer ** 

This repository contains 2 slack bots to help organizing lunch time.
* restaurantOrganizer : creates groups and designate a friend in charge of booking the restaurant.
* pizzaOrganizer : creates a list gathering all pizza requests of your friends to help.

Those bots are freely inpired from this tutorial : 
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
(This tutorial also helps you understanding what virtualenv is useful for...)

To use the bot you need to install slackclient (via pip for instance) :
pip install slackclient


* Launch bot deamon : 
-----------------------
From a terminal :
python restaurantorganizer.py API_TOKEN --waiting_time 20
python pizzaOrganizer.py API_TOKEN --waiting_time 20

(Launches the bots and let 20 minutes for people to answer)

https://gopro.slack.com/services/B2K6XE1L7 under API TOKEN

* Invoke bot in slack : 
-----------------------
If the bot is not already present in the targeted channel, add it to the channel.
And then type : 
@restaurant-organizer organize
@pizza-organizer organize
