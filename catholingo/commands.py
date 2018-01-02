#!/usr/bin/python3
#coding: utf8

import os
import redis
import time
import json

class StopAndTalkException(Exception):
	pass

class TextOrder(object):
	CONFIG_PREFIX = "catholingo_config_"

	def _redis(self):
		return redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)), db=0)

	def connect(self):
		self.pubsub = self._redis().pubsub()
		self.pubsub.subscribe(os.environ.get('CATHOLINGO_REDIS_ORDER_CHANNEL', 'catholingo_order'))
		self.client = CommandExecute()

	def run(self):
		self.connect()
		while True:
			message = self.pubsub.get_message()
			if message:
				self.parse_message(message)
			time.sleep(0.01)

	def parse_message(self, message):
		data = message.get('data')
		if type(data) is bytes:
			data = data.decode('utf-8').split()
			try:
				self.action(data[0], data[1], data[2:])
			except StopAndTalkException as e:
				self.client.message(data[0], str(e))

	def action(self, source, target, message):
		pass

	def config(self, label, default=None):
		value = self._redis().get(self.CONFIG_PREFIX+label)
		if value:
			return value.decode('utf-8')
		return default

	def set_config(self, label, value):
		return self._redis().set(self.CONFIG_PREFIX+label, str(value))

class CommandOrder(TextOrder):
	COMMAND = "!test"

	def __init__(self):
		if type(self.__class__.COMMAND) is not list:
			self.__class__.COMMAND = [self.__class__.COMMAND]
		self.__class__.COMMAND = [c[1:] if c[0] == "!" else c for c in self.__class__.COMMAND]

	def action(self, source, target, message):
		if message[0][1:] in self.__class__.COMMAND:
			return self.command(source, target, message[1:])

	def command(self, source, target, message):
		pass

class TalkativeCommandOrder(CommandOrder):
	def talk(self, source, target, message):
		return ""

	def command(self, source, target, message):
		payload = self.talk(source, target, message)
		if payload:
			raise StopAndTalkException(payload)

class TalkativeTextOrder(TextOrder):
	def talk(self, source, target, message):
		return ""

	def action(self, source, target, message):
		payload = self.talk(source, target, message)
		if payload:
			raise StopAndTalkException(payload)

class OrderPool(TextOrder):
	def __init__(self, orders):
		self.orders = [o if isinstance(o, TextOrder) else o() for o in orders]

	def parse_message(self, message):
		for order in self.orders:
			order.client = self.client
			order.parse_message(message)

def AdminCommandOrder(CommandOrderCls):
	class AdminCommandOrderCls(CommandOrderCls):
		def command(self, source, target, message):
			for admins in (self.config('ADMINS_'+self.__class__.COMMAND[0]),
						   self.config('ADMINS'),
						   os.environ.get('CATHOLINGO_ADMIN_NICKNAME')):
				if admins and target in admins.split():
					return super().command(source, target, message)
			raise StopAndTalkException("Command reserved to admin")
	return AdminCommandOrderCls

class CommandExecute(object):
	def __getattr__(self, method):
		def execute(*args, **kwargs):
			payload = json.dumps(dict(method=method, args=args, kwargs=kwargs))
			r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)), db=0)
			return r.publish(os.environ.get('CATHOLINGO_REDIS_EXECUTE_CHANNEL', 'catholingo_execute'), payload)
		return execute
