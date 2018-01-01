#!/usr/bin/python3
#coding: utf8

import datetime
import json
import random
import time
from qhue import Bridge
from threading import Thread
from commands import TalkativeCommandOrder, TextOrder, OrderPool, StopAndTalkException

BRIDGE_HOST_CONFIG = "HUE_BRIDGE_HOST"
BRIDGE_USERNAME_CONFIG = "HUE_USERNAME" # aoFVhPv0DRBtX47bg1PLsNMPStMfInwQfhQ9ImjW

def generate_color():
    charset = '0123456789ABCDEF'
    return "".join([random.choice(charset) for _ in range(6)])

def hexa_to_rgb(color):
    try:
        return (int('0x'+color[i:i+2], base=16) for i in range(0, len(color), 2))
    except:
        return (0, 0, 0)

def gamma_correction(c):
	return pow((c+0.055) / 1.055, 2.4) if c > 0.04045 else (c / 12.92)

# this is magic
def rgb_to_xy(r,g,b):
	r = gamma_correction(r)
	g = gamma_correction(g)
	b = gamma_correction(b)
	# Apply wide gamut conversion D65
	x = r * 0.664511 + g * 0.154324 + b * 0.162028
	y = r * 0.283881 + g * 0.668433 + b * 0.047685
	z = r * 0.000088 + g * 0.072310 + b * 0.986039
	try:
		fx = x / (x+y+z)
		fy = y / (x+y+z)
	except:
		fx = 0.0
		fy = 0.0
	return [fx, fy]

class HueBase(TalkativeCommandOrder):
    def init(self):
        self.host = self.config(BRIDGE_HOST_CONFIG)
        self.username = self.config(BRIDGE_USERNAME_CONFIG)

        if not self.host:
            raise StopAndTalkException("Bridge host not configured. Usage: !config "+BRIDGE_HOST_CONFIG+" <host> (e.g. 192.168.1.x, ...)")
        if not self.username:
            raise StopAndTalkException("Username not configured. Usage: !config "+BRIDGE_USERNAME_CONFIG+" <username>")

        self.bridge = Bridge(self.host, self.username)

class ColorCommand(HueBase):
    COMMAND = ["!color", "!colour", "!rgb"]

    def talk(self, source, target, message):
        self.init()
        ERR_MSG = "Usage: "+self.COMMAND[0]+" <light index> <RGB>"
        if len(message) < 2:
            return ERR_MSG
        if len(message[1]) != 6:
            return ERR_MSG

        light = message[0]
        color = message[1]
        r, g, b = hexa_to_rgb(color)
        try:
            self.bridge.lights[light].state(xy=rgb_to_xy(r,g,b))
        except:
            return "Failed :("
        return color+" \o/"

class BrightnessCommand(HueBase):
    COMMAND = ["!brightness", "!bri", "!bright"]

    def talk(self, source, target, message):
        self.init()
        ERR_MSG = "Usage: "+self.COMMAND[0]+" <light index> <0-255>"
        if len(message) < 2:
            return ERR_MSG

        light = message[0]
        bri = message[1]
        try:
            bri = int(bri)
        except:
            return ERR_MSG
        if bri < 0 or bri > 255:
            return ERR_MSG

        try:
            self.bridge.lights[light].state(bri=bri)
        except:
            return "Failed :("
        return str(bri)+" \o/"

class LightCommand(HueBase):
    COMMAND = "!light"

    def talk(self, source, target, message):
        self.init()
        ERR_MSG = "Usage: "+self.COMMAND[0]+" <light index> <on/off>"
        if len(message) < 2:
            return ERR_MSG

        light = message[0]
        mode = message[1]
        if mode not in ["on", "off"]:
            return ERR_MSG

        try:
            self.bridge.lights[light].state(on=mode == "on")
        except:
            return "Failed :("
        return mode+" \o/"

class PartyThread(Thread):
    def __init__(self, light, duration, interval, bridge):
        super().__init__()
        self.light = light
        self.duration = duration
        self.interval = interval
        self.bridge = bridge

    def run(self):
        nbcolors = self.duration // self.interval
        colors = (generate_color() for __ in range(nbcolors))
        for color in colors:
            r,g,b = hexa_to_rgb(color)
            xy = rgb_to_xy(r,g,b)
            self.bridge.lights[self.light].state(on=True, xy=xy)
            time.sleep(self.interval)

class PartyCommand(HueBase):
    COMMAND = "!party"

    def talk(self, source, target, message):
        self.init()
        ERR_MSG = "Usage: "+self.COMMAND[0]+" <light index> <duration> <interval>"
        if len(message) < 3:
            return ERR_MSG
        light = message[0]
        try:
            duration = int(message[1])
            interval = int(message[2])
        except:
            return ERR_MSG

        PartyThread(light, duration, interval, self.bridge).start()
        return "PARTY \o/"
if __name__ == '__main__':
	pool = OrderPool(orders=[ColorCommand, BrightnessCommand, LightCommand, PartyCommand])
	pool.run()
