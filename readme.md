# Raspberry Pi Appointment Reminder HD - Notify Edition

## Tasks

+ Move readme content to Wiki
+ Remove milliseconds from log output (it's just not needed)
+ Clean up all imports
+ Add Troubleshooting section to the Wiki
+ Move search limit (time) to the config file

If modifying these scopes, delete the file token.pickle.

Install Unicorn HAT software
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dateutil

Project relies upon two external services:

+ Google Calendar
+ Particle Cloud 

Multiple Remind projects:

+ Pi Remind
+ Pi Remind Blinkit
+ Pi Remind HD (archived, point to this one)
+ Pi Remind HD Notify

Copy `config.rename` to `config.json`
you'll want to keep the original around as a reference methinks

```json
{
  "access_token": "",
  "device_id": "",
  "ignore_tentative_appointments": false,
  "use_reboot_counter": false,
  "reboot_counter_limit": 10,
  "use_remote_notify": false,
  "debug_mode": false
}
```

---

The project is an enhancement to the [Pi Remind HD](https://github.com/johnwargo/pi-remind-hd) project enabling it to work with the [Remote Notify](https://github.com/johnwargo/particle-remote-notify-rgb) project. 

The Pi Remind project connects to a user's Google Calendar, then displays appointment reminders on a [Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd).
In this project, the status of the user's Google Calendar is also sent to the Remote Notify device, lighting a LED Red when the user is busy (based on the calendar), Yellow for tentative, and Green for free/available.

Complete project setup instructions for the Pi Remind HD Notify project are in the project repository's [Wiki](https://github.com/johnwargo/pi-remind-hd-notify/wiki). Setup instructions for the Remote Notify device are in that project's [Wiki](https://github.com/johnwargo/particle-remote-notify-rgb/wiki).

## MOVE TO WIKI

Put this content in the Wiki

# Raspberry Pi Appointment Reminder (HD)

I often find myself missing appointments because I'm engrossed in my work or because I've switched to a different computer and can't hear the reminder ping on my work laptop. I created this project to give me a visual reminder, an obnoxious, silent countdown timer I can set on my desk to flash lights at me as a warning before my next meeting starts.

The project uses a network connected Raspberry Pi and a [Pimoroni Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd) to flash the reminder. The project was originally built using the Pimoroni Unicorn HAT, and published in Make Magazine (makezine.com): [Get a Flashing Meeting Reminder with a Raspberry Pi](http://makezine.com/projects/get-a-flashing-meeting-reminder-with-a-raspberry-pi/). For this version, I upgraded the Unicorn HAT to the High Definition (HD) version which will allow me to display much cleaner and more interesting color patterns. The HD version of the Unicorn HAT has 256 LEDs vs the original Unicorn HAT's 64, for much higher pixel resolution.

One of the things I wanted to do in the original project was display the meeting description/subject on the Unicorn HAT. I could have done it, but because of the low pixel resolution of the Unicorn HAT, it would have looked clunky. The Unicorn HAT HD has a higher pixel resolution, so I've added the feature here.

## Alerts

The Pi connects to Google Calendar and checks every minute for upcoming appointments then flashes the Unicorn HAT's LEDs for following alerts:

* **White** @ 10 minutes until 5 minutes
* **Yellow** @ 5 minutes until 2 minutes
* **Multi-color swirl** @ 2 minutes

If you're feeling adventurous, you can change the code to use any of the sample patterns included with the [Unicorn HAT HD Sample Code](https://github.com/pimoroni/unicorn-hat-hd/tree/master/examples).  I'm personally a big fan of the star field example, but that's not very useful as an alerting mechanism.

## Indicator LED

The project displays a single indicator LED to let you know the app is working. It will illuminate a single LED along the bottom row of the Unicorn HAT and move the LED across the display every time it connects to Google to obtain calendar information. The color of the LED indicates status of the app as well:

* **Blue** - The app is connecting to the Google Calendar API
* **Green** - The app received data from the Google Calendar API, but there are no pending appointments within the next 10 minutes
* **Red** - The app encountered an error connecting to the Google Calendar API
* **White** - There is an appointment beginning within 10 minutes
* **Yellow** - There is an appointment beginning within the next 5 minutes
* **Orange** - There is an appointment beginning within the next 2 minutes

This way, even if you miss the flashing lights, you can glance at the display and still determine if you have an upcoming appointment.

## Required Components

For this project, I used the following components:

* [Raspberry Pi 3](https://www.raspberrypi.org/), but most any Pi will work. Check the Unicorn HAT documentation for supported Pi devices.
* [Pimoroni Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd)
* [Adafruit Raspberry Pi B+ / Pi 2 / Pi 3 Case - Smoke Base - w/ Clear Top](https://www.adafruit.com/products/2258)
* [CanaKit 5V 2.5A Raspberry Pi 3 Power Supply / Adapter / Charger (UL Listed)](http://www.amazon.com/CanaKit-Raspberry-Supply-Adapter-Charger/dp/B00MARDJZ4) from Amazon

## Google Calendar API Setup

Before you start, you must setup an account with Google so the app can consume the Google Calendar APIs used by the project. To setup your account, read the [Google Calendar API Python Quickstart](https://developers.google.com/google-apps/calendar/quickstart/python).

At the conclusion of the Google account setup process, download your Google Calendar API application's `client_secret.json` file, you'll need to copy the file to the Pi Reminder project folder later.. Be sure to name the downloaded file using that file name. The project's code uses this file to authorize access your Google Calendar and that file name is hard coded into the project's Python app. The file will contain a big random number in its file name, just rename it to `client_secret.json`.

## Raspberry Pi Setup

We'll start by connecting all the hardware, then move on to the software setup.

### Hardware

To setup the hardware, complete the following steps:

1. Mount the Pimoroni Unicorn HAT HD on the Raspberry Pi device using the included hardware
2. Place the Pi in a case
3. Power it up!

That's it, you're done. That was easy! When you're done, the Pi will look something like the following:

![Raspberry Pi Configuration Hardware Assembly](screenshots/figure-01.png)

**Note:** The Unicorn HAT HD has a smoked lens that hides the actual LED elements, so you can't really see the HAT in the case. It's a much cleaner, more professional look than my previous reminder projects.

When the Pi boots up, log into the Pi using the default credentials (`pi`/`raspberry`). Next, you must change the Pi's hardware configuration so it can talk to the Unicorn HAT HD using the SPI protocol. Open the Pi menu (located in the upper-left corner of the screen), select **Preferences**, then **Raspberry Pi Configuration**. In the application that opens, select the **Interfaces** tab, then enable the **SPI** option as shown in the following figure:

![Raspberry Pi Configuration Utility](screenshots/figure-02.png)

Click the **OK** button to save your changes.  You should **not** have to reboot your Pi after completing this step.

### Software

When the Pi is all ready to go, open a terminal window and update the device's software using the following commands:

```shell
sudo apt-get update
sudo apt-get upgrade
```

> Note: More recent versions of the Raspbian OS automatically check for updates on first launch, so the previous step is probably no longer necessary. If you're using a Pi that's been running for a while, it's always best to install all updates when you get a chance.

The first command updates the local software repositories and the second command updates the Pi's Raspbian OS and associated files.

Next, install the [Google Calendar API Python files](https://developers.google.com/api-client-library/python/start/installation) along with some date handling libraries using the following command:

```shell
pip install --upgrade google-api-python-client oauth2client python-dateutil pytz
```

> Note: The original version of this project used `sudo` to install Python libraries, but that's no longer necessary.

Install the Unicorn HAT libraries following the instructions on the [Pimoroni web site](https://github.com/pimoroni/unicorn-hat-hd). Basically, open a terminal window and execute the following command:

```shell
curl -sS get.pimoroni.com/unicornhathd | bash
```

Next, download the project's code; in the same terminal window, execute the following commands:

```shell
git clone https://github.com/johnwargo/pi-remind-hd
cd pi-remind-hd
ls
```

If all goes well, you should see the following files in the folder:

* `screenshots` (folder)
* `changelog.md`
* `LICENSE`
* `readme.md` (this file)
* `remind.py`
* `start-remind.sh`

> Note: You only need the `remind.py` and `start-remind.sh` files to run this project on the Raspberry Pi; the remaining files are just documentation.  If you want to, you can delete the other files and the one folder to free up space on your Pi.

Copy your personal Google Calendar project's `client_secret.json` file (downloaded when you created your Google account) to the `pi-remind-hd` folder you just created. With everything in place, execute the reminder app using the following command:

```shell
python ./remind.py
```

Before the app can access the calendar, you'll need to authorize the app to use the Google Calendar API for your calendar account. When you launch the app for the first time (using the command shown above) the browser will launch and walk you through the process. With that complete, PI Remind should start watching your calendar for events.

## Starting The Project Application Automatically

There are a few steps you must complete to configure the Raspberry Pi so it executes the the reminder app on startup. You can read more about this here: [Autostart Python App on Raspberry Pi in a Terminal Window](http://johnwargo.com/index.php/microcontrollers-single-board-computers/autostart-python-app-on-raspberry-pi-in-a-terminal-window.html).

>**Note:** Don't forget to authorize the Google Calendar API to access your Google Calendar by running the manual startup process described in the previous session before enabling autostart.

If you don't already have a terminal window open, open one, then navigate to the folder where you extracted the project files (if you followed my earlier instructions, you should have the files in `/home/pi/pi-remind-hd/`). Make the project's bash script file executable by executing the following command:

```shell
chmod +x ./start-remind.sh
```

Next, you'll need to open the pi's `autostart` file using the following command:  

```shell
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Add the following lines to the end (bottom) of the file:

```shell
@lxterminal -e /home/pi/pi-remind-hd/start-remind.sh
```

To save your changes, press **Ctrl-o** then press the Enter key. Next, press **Ctrl-x** to exit the `nano` application.

Reboot the Raspberry Pi; when it restarts, the python remind process should launch and execute in its own terminal window.

> **Note**: Because of the way we're starting this terminal process on startup, every time a user logs into the Pi, it will launch a terminal window for that user and run the `remind.py` script. This shouldn't matter when you're running the pi headless (with no monitor and keyboard), but when you remote into the Pi (using something like Windows Remote Desktop), your remote session will get its own version of the Remind application. In the initial version of this project, I included instructions to edit the user's `autostart` file: `sudo nano ~/.config/lxsession/LXDE-pi/autostart` but that file no longer exists on current versions of the Raspbian OS.

## Changing the Google Profile

If you need to change the Google profile used by the Remind app, complete the following steps:

1. Login to your Raspberry Pi device
2. In the terminal window running `remind.py`, press CTRL-C to stop the process
3. Open the Pi's File Manager and navigate to the `pi-remind-hd` folder shown in the following figure
4. Delete the `google-api-token.json` file
5. Run the `remind.py` application using the instructions above to configure the new profile.

![File Explorer](screenshots/figure-03.png)

## Revisions & Updates

See the [Changelog](changelog.md).

## Known Issues

* Reminders are triggered for canceled events. If you have your Google Calendar configured to show deleted events, `pi_remind` will flash its lights for those events as well. I've tried setting `showDeleted` to `false` in the API call that gets the calendar entry list from Google, but it does not seem to have an effect (in my testing anyway).

***

If you find this code useful, and feel like thanking me for providing it, please consider making a purchase from [my Amazon Wish List](https://amzn.com/w/1WI6AAUKPT5P9). You can find information on many different topics on my [personal blog](http://www.johnwargo.com). Learn about all of my publications at [John Wargo Books](http://www.johnwargobooks.com).



***

If you find this code useful, and feel like thanking me for providing it, please consider making a purchase from [my Amazon Wish List](https://amzn.com/w/1WI6AAUKPT5P9). You can find information on many different topics on my [personal blog](http://www.johnwargo.com). Learn about all of my publications at [John Wargo Books](http://www.johnwargobooks.com).
