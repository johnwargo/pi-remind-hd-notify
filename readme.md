# Raspberry Pi Appointment Reminder HD - Notify Edition

Copy `config.rename` to `config.json`

# If modifying these scopes, delete the file token.pickle.

Install Unicorn HAT software
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install python-dateutil

Project relies upon two external services:

+ Google Calendar
+ Particle Cloud 

Add Troubleshooting section

Multiple Remind projects:

+ Pi Remind
+ Pi Remind Blinkit
+ Pi Remind HD (archived, point to this one)
+ Pi Remind HD Notify

The project is an enhancement to the [Pi Remind HD](https://github.com/johnwargo/pi-remind-hd) project enabling it to work with the [Remote Notify](https://github.com/johnwargo/particle-remote-notify-rgb) project. 

The Pi Remind project connects to a user's Google Calendar, then displays appointment reminders on a [Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd).
In this project, the status of the user's Google Calendar is also sent to the Remote Notify device, lighting a LED Red when the user is busy (based on the calendar), Yellow for tentative, and Green for free/available.

Complete project setup instructions for the Pi Remind HD Notify project are in the project repository's [Wiki](https://github.com/johnwargo/pi-remind-hd-notify/wiki). Setup instructions for the Remote Notify device are in that project's [Wiki](https://github.com/johnwargo/particle-remote-notify-rgb/wiki).


***

If you find this code useful, and feel like thanking me for providing it, please consider making a purchase from [my Amazon Wish List](https://amzn.com/w/1WI6AAUKPT5P9). You can find information on many different topics on my [personal blog](http://www.johnwargo.com). Learn about all of my publications at [John Wargo Books](http://www.johnwargobooks.com).
