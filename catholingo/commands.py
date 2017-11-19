#!/usr/bin/python3
#coding: utf8

import os
import pydle
import redis
import speechdb
import time
import json
from speechdb import Speech, Word

class CommandOrder(object):
	COMMAND = "!test"

	def __init__(self):
		if type(self.__class__.COMMAND) is not list:
			self.__class__.COMMAND = [self.__class__.COMMAND]
		self.__class__.COMMAND = [c[1:] if c[0] == "!" else c for c in self.__class__.COMMAND]

	def connect(self):
		r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)), db=0)
		self.pubsub = r.pubsub()
		self.pubsub.subscribe(os.environ.get('CATHOLINGO_REDIS_ORDER_CHANNEL', 'catholingo_order'))
		self.client = CommandExecute()

	def run(self):
		self.connect()
		while True:
			message = self.pubsub.get_message()
			if message:
				self.parse_message(message)
			time.sleep(1)

	def parse_message(self, message):
		data = message.get('data')
		if type(data) is bytes:
			data = data.decode('utf-8').split()
			if data[2][1:] in self.__class__.COMMAND:
				self.command(data[0], data[1], data[3:])

	def command(self, source, target, message):
		pass

class TalkativeCommandOrder(CommandOrder):
	def talk(self, source, target, message):
		return ""

	def command(self, source, target, message):
		payload = self.talk(source, target, message)
		if payload:
			self.client.message(source, str(payload))

class CommandOrderPool(CommandOrder):
	def __init__(self, commands):
		self.commands = [c if type(c) == CommandOrder else c() for c in commands]

	def parse_message(self, message):
		for command in self.commands:
			command.client = self.client
			command.parse_message(message)

class CommandExecute(object):
	def __getattr__(self, method):
		def execute(*args, **kwargs):
			payload = json.dumps(dict(method=method, args=args, kwargs=kwargs))
			r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)), db=0)
			return r.publish(os.environ.get('CATHOLINGO_REDIS_EXECUTE_CHANNEL', 'catholingo_execute'), payload)
		return execute

if __name__ == '__main__':
	if os.environ.get('DEBUG'):
		import logging
		logger = logging.getLogger('peewee')
		logger.setLevel(logging.DEBUG)
		logger.addHandler(logging.StreamHandler())
	CommandOrder().run()
