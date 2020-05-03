# Raspberry Pi Appointment Reminder HD - Notify Edition

## Tasks

+ Move readme content to Wiki
+ Archive the Pi-Remind-HD project and point to this one
+ Add Troubleshooting section to the Wiki
+ Move search limit (time) to the config file

If modifying these scopes, delete the file token.pickle.

Install Unicorn HAT software
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dateutil

Project relies upon two external services:

+ Google Calendar
+ Particle Cloud 



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

debug is cool because it outputs everything the app is doing
Since the Google Calendar uses it as well, you get output from that library as well

How working hours work

---

The project is an enhancement to the [Pi Remind HD](https://github.com/johnwargo/pi-remind-hd) project enabling it to work with the [Remote Notify](https://github.com/johnwargo/particle-remote-notify-rgb) project. 

The Pi Remind project connects to a user's Google Calendar, then displays appointment reminders on a [Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd).
In this project, the status of the user's Google Calendar is also sent to the Remote Notify device, lighting a LED Red when the user is busy (based on the calendar), Yellow for tentative, and Green for free/available.

Complete project setup instructions for the Pi Remind HD Notify project are in the project repository's [Wiki](https://github.com/johnwargo/pi-remind-hd-notify/wiki). Setup instructions for the Remote Notify device are in that project's [Wiki](https://github.com/johnwargo/particle-remote-notify-rgb/wiki).





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
