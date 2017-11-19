#!/usr/bin/python3
#coding: utf8

import os
import pydle
import redis
import time
import json
import sys
from threading import Thread

class CommandListener(Thread):
	def __init__(self, client):
		Thread.__init__(self)
		self.client = client

	def run(self):
		r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)), db=0)
		self.pubsub = r.pubsub()
		self.pubsub.subscribe(os.environ.get('CATHOLINGO_REDIS_EXECUTE_CHANNEL', 'catholingo_execute'))
		while True:
			message = self.pubsub.get_message()
			if message:
				self.parse_message(message)
			time.sleep(1)

	def parse_message(self, message):
		data = message.get('data')
		if type(data) is bytes:
			data = json.loads(data.decode('utf-8'))
			method = data.get('method')
			args = data.get('args', list())
			kwargs = data.get('kwargs', dict())
			if hasattr(self.client, method):
				return getattr(self.client, method)(*args, **kwargs)

class CommandOrder(object):
	def order(self, channel, user, message):
		r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)), db=0)
		return r.publish(os.environ.get('CATHOLINGO_REDIS_ORDER_CHANNEL', 'catholingo_order'), " ".join([channel, user, message]))

class CathoLingo(pydle.Client):
	def on_connect(self):
		for chan in os.environ.get('CHANNELS', '#amdo').split():
			self.join(chan)

	def on_message(self, source, target, message):
		self.command(source, target, message)

	def command(self, source, target, message):
		command = CommandOrder()
		command.order(source, target, message)

if __name__ == '__main__':
	client = CathoLingo(os.environ.get('USERNAME', 'CathoLingo'), realname=os.environ.get('REALNAME', 'la pizzeria'))
	client.connect(os.environ.get('IRC_HOST', 'chat.freenode.net'), int(os.environ.get('IRC_PORT', 6697)), tls=True, tls_verify=False)
	CommandListener(client).start()
	client.handle_forever()
