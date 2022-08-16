# Changelog

## 2022-08-16

* Added runtime error handler to `remind.py`
* Close log file on any error

## 2020-06-16

Added a file logger (`remind_log`) to the project. With this change, output level to the console is controlled by the config setting, but the file logger always writes debug output. The code keeps 7 days of log files, rotating at midnight.

## 2020-06-03

Created a Settings class and abstracted all config options there. This makes the code less klunky. I originally read all the config settings in `remind.py` then passed them to the google calendar module during init. That was fine when I only had one or two settings to pass there, but ridiculous after I'd added so many. 

This change is my first attempt at implementing the Singleton pattern in Python. it's also the first time I ever used assertions (`assert`) in a Python application. 

## 2020-05-21

Fixed a bug I created through the refactor. if the Pi loses network connectivity, the app crashed spectacularly. It turns out that I forgot to return a value from the Try/Catch (which I added back in this release)

## 2020-05-18

+ Added an option to ignore appointment summaries that contain specific values:

```json
"ignore_in_summary": ["[block]", "(via clockwise)", "[anna]", "[august]", "[elizabeth]"],
```

## 2020-05-01

+ Refactored the app, moving the Google Calendar and Unicorn HAT stuff to separate modules
+ Added a Particle Cloud module
+ Moved configuration settings from the code to an included `config.json` file
+ Replaced all `print` statements with Python Logging
+ Added ability to control the [Fumbly Stuff](https://fumblystuff.com) Remote Notify device whenever your calendar availability changes
+ Moved installation, configuration, and usage instructions from the readme file to the project's Wiki
+ Added support for Working Hours

 