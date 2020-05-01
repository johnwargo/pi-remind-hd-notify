###########################################################
#  Unicorn HAT module
#
# exposes properties and methods for the Unicorn HAT LED
# array
###########################################################
# TODO: Make this into a singleton

import math
import time
import unicornhathd

# TODO: Clean up imports
# import pytz
# from dateutil import parser
# from googleapiclient.discovery import build
# from httplib2 import Http
# from oauth2client import client, file, tools

# =======================================================================================
# Borrowed from: https://github.com/pimoroni/unicorn-hat-hd/blob/master/examples/text.py
# =======================================================================================
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    exit("This script requires the pillow module\nInstall with: sudo pip install pillow")

# Use `fc-list` to show a list of installed fonts on your system,
# or `ls /usr/share/fonts/` and explore.

FONT = ("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 12)
# =======================================================================================

# COLORS
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 153, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# constants used in the app to display status
CHECKING_COLOR = BLUE
SUCCESS_COLOR = GREEN
FAILURE_COLOR = RED

current_activity_light = 0
indicator_row = 0
u_height = 0
u_width = 0


def init():
    global current_activity_light, indicator_row, u_height, u_width

    # Clear the display (just in case)
    unicornhathd.clear()
    # Initialize  all LEDs to black
    unicornhathd.set_all(0, 0, 0)
    # set the display orientation to zero degrees
    unicornhathd.rotation(90)
    # set u_width and u_height with the appropriate parameters for the HAT
    u_width, u_height = unicornhathd.get_shape()
    # calculate where we want to put the indicator light
    indicator_row = u_height - 1

    # The app flashes a GREEN light in the first row every time it connects to Google to check the calendar.
    # The LED increments every time until it gets to the other side then starts over at the beginning again.
    # The current_activity_light variable keeps track of which light lit last. At start it's at -1 and goes from there.
    current_activity_light = u_width

    # Set a specific brightness level for the Pimoroni Unicorn HAT, otherwise it's pretty bright.
    # Comment out the line below to see what the default looks like.
    unicornhathd.brightness(0.5)


def display_text(message, color=WHITE):

    global u_height, u_width

    # do we have a message?
    if len(message) > 0:
        # then display it
        # code borrowed from: https://github.com/pimoroni/unicorn-hat-hd/blob/master/examples/text.py
        text_x = u_width
        text_y = 2

        font_file, font_size = FONT

        font = ImageFont.truetype(font_file, font_size)

        # =====================================================================
        # I'm really not sure what all this code does...that's what happens when you 'borrow' code
        # it basically sets up the width of the display string to include the string as well as enough
        # space to scroll it off the screen
        # =====================================================================
        text_width, text_height = u_width, 0
        w, h = font.getsize(message)
        text_width += w + u_width
        text_height = max(text_height, h)
        text_width += u_width + text_x + 1
        image = Image.new("RGB", (text_width, max(16, text_height)), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        offset_left = 0
        draw.text((text_x + offset_left, text_y), message, color, font=font)
        offset_left += font.getsize(message)[0] + u_width
        for scroll in range(text_width - u_width):
            for x in range(u_width):
                for y in range(u_height):
                    pixel = image.getpixel((x + scroll, y))
                    r, g, b = [int(n) for n in pixel]
                    unicornhathd.set_pixel(u_width - 1 - x, y, r, g, b)
            unicornhathd.show()
            time.sleep(0.01)
        unicornhathd.off()
        # =====================================================================


def swirl(x, y, step):
    global u_height, u_width

    # modified from: https://github.com/pimoroni/unicorn-hat-hd/blob/master/examples/demo.py
    x -= (u_width / 2)
    y -= (u_height / 2)
    dist = math.sqrt(pow(x, 2) + pow(y, 2)) / 2.0
    angle = (step / 10.0) + (dist * 1.5)
    s = math.sin(angle)
    c = math.cos(angle)
    xs = x * c - y * s
    ys = x * s + y * c
    r = abs(xs + ys)
    r = r * 12.0
    r -= 20
    return r, r + (s * 130), r + (c * 130)


def do_swirl(duration):
    # modified from: https://github.com/pimoroni/unicorn-hat-hd/blob/master/examples/demo.py
    step = 0
    for i in range(duration):
        for y in range(u_height):
            for x in range(u_width):
                r, g, b = swirl(x, y, step)
                r = int(max(0, min(255, r)))
                g = int(max(0, min(255, g)))
                b = int(max(0, min(255, b)))
                unicornhathd.set_pixel(x, y, r, g, b)
        step += 2
        unicornhathd.show()
        time.sleep(0.01)
    # turn off all lights when you're done
    unicornhathd.off()


def set_activity_light(color, increment):
    # used to turn on one LED at a time across the bottom row of lights. The app uses this as an unobtrusive
    # indicator when it connects to Google to check the calendar. Its intended as a subtle reminder that things
    # are still working.
    global current_activity_light
    # turn off (clear) any lights that are on
    unicornhathd.off()
    if increment:
        # OK. Which light will we be illuminating?
        if current_activity_light < 1:
            # start over at the beginning when you're at the end of the row
            current_activity_light = u_width
        # increment the current light (to the next one)
        current_activity_light -= 1
    # set the pixel color
    unicornhathd.set_pixel(current_activity_light, indicator_row, *color)
    # show the pixel
    unicornhathd.show()


def set_all(color):
    unicornhathd.set_all(*color)
    unicornhathd.show()


def flash_all(flash_count, delay, color):
    # light all of the LEDs in a RGB single color. Repeat 'flash_count' times
    # keep illuminated for 'delay' value
    for index in range(flash_count):
        # fill the light buffer with the specified color
        unicornhathd.set_all(*color)
        # show the color
        unicornhathd.show()
        # wait a bit
        time.sleep(delay)
        # turn everything off
        unicornhathd.off()
        # wait a bit more
        time.sleep(delay)


def flash_random(flash_count, delay, between_delay=0):
    # Copied from https://github.com/pimoroni/unicorn-hat-hd/blob/master/examples/test.py
    for index in range(flash_count):
        # fill the light buffer with random colors
        unicornhathd._buf = unicornhathd.numpy.random.randint(low=0, high=255, size=(16, 16, 3))
        # show the colors
        unicornhathd.show()
        # wait a bit
        time.sleep(delay)
        # turn everything off
        unicornhathd.off()
        # do we have a between_delay value??
        if between_delay > 0:
            # wait a bit more
            time.sleep(between_delay)


def off():
    unicornhathd.off()
