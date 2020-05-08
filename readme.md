# Raspberry Pi Appointment Reminder HD - Notify Edition

> **Note:** This project is still in active development, so there's still some things I need to do to finish it up.

## Tasks

* Validate that the config file will validate if the access token or device ID are empty.
* Finish the working hours implementation
* Add Troubleshooting section to the Wiki
* Move search limit (time) to the config file (not gonna happen soon)

The Pi Remind project connects to a user's Google Calendar, then displays appointment reminders on a [Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd) LED array.

> **Note:** Assembly, Installation, Configuration, and Operation instructions are all published to the [Wiki](https://github.com/johnwargo/pi-remind-hd-notify/wiki)

The project is the latest version of Pi Remind, a Raspberry Pi-based project for notifying users of upcoming appointments in Google Calendar. I built this project because I often missed appointments because I was engrossed in my work or because I switched away from my work computer to a different one and didn't hear the reminder ping on my work laptop. I created this project to give me a visual reminder, an obnoxious, silent, countdown timer I can set on my desk to flash lights at me as a warning before my next meeting starts.

There are several versions of this project:

+ [Pi Remind](https://github.com/johnwargo/pi-remind) - The original, used the low resolution Pimoroni Unicorn HAT to display notifications and didn't show the meeting title because the resolution was too low (8x8 LED matrix).
+ [Pi Remind Blinkit](https://github.com/johnwargo/pi-remind-zero-blinkt) - A version of the project for the Raspberry Pi Zero and the Pimoroni [Pi Zero W Starter Kit](https://shop.pimoroni.com/products/pi-zero-w-starter-kit)
+ [Pi Remind HD](https://github.com/johnwargo/pi-remind-hd) - For this version of the project, I upgraded to the Pimoroni Unicorn HAT HD which upgraded the LED matrix to a 64x64 grid of LEDs and enabled me to display the appointment subject during a notification (it scrolls by on the matrix)
+ Pi Remind HD Notify (this project) - For this version of the project, I completely refactored the code, separating the Unicorn HAT and Google Calendar code to separate libraries. I also pulled all the configuration settings (but one) to an external file so you can configure the app's behavior without modifying the code and maintain them after a project update (you're welcome). 

The biggest change in this version of the project is that Pi Remind now works with the soon to be released Remote Notify device from [Fumbly Stuff](https://fumblystuff.com). Remote Notify is basically a remote controlled RGB LED you can use to let family members know  your availability for interruption; you can see an image of the current prototype in the following image. With this version of Pi Remind, you can configure it to update your Remote Notify device whenever your availability status changes based on your calendar.

![Remote Notify Prototype](https://github.com/johnwargo/pi-remind-hd-notify/blob/master/images/remote-notify-prototype.png)

Pi Remind uses a network connected Raspberry Pi and a [Pimoroni Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd) to flash the reminder. The project was originally built using the Pimoroni Unicorn HAT, and published in Make Magazine (makezine.com): [Get a Flashing Meeting Reminder with a Raspberry Pi](http://makezine.com/projects/get-a-flashing-meeting-reminder-with-a-raspberry-pi/). For this version, I upgraded the Unicorn HAT to the High Definition (HD) version which will allow me to display much cleaner and more interesting color patterns. The HD version of the Unicorn HAT has 256 LEDs vs the original Unicorn HAT's 64, for much higher pixel resolution.

Next, head over to the  [Wiki](https://github.com/johnwargo/pi-remind-hd-notify/wiki) to learn how to assemble, install, configure, and use this project.

> **Note:** This software is provided as is, with no support or warranty. If you have an issue with the project, don't call or email me, use the project's [Issues](https://github.com/johnwargo/pi-remind-hd-notify/issues) area to ask your questions. I usually check email at least once a day and will respond as soon as I can. Posting to the issues page also lets other users learn about potential issues and even jump in and help you solve it.

***

If you find this code useful, and feel like thanking me for providing it, please consider making a purchase from [my Amazon Wish List](https://amzn.com/w/1WI6AAUKPT5P9). You can find information on many different topics on my [personal blog](http://www.johnwargo.com). Learn about all of my publications at [John Wargo Books](http://www.johnwargobooks.com).
