#!/usr/bin/python3
#coding: utf8

import os
import pydle
import redis
import speechdb
import time
import json
import sys
from speechdb import Speech, Word
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
		self.save_speech(source, target, message)
		self.command(source, target, message)

	def command(self, source, target, message):
		command = CommandOrder()
		if "catholingo" in message.lower():
			command.order(source, target, "!speak")
		elif message[0] == "!":
			command.order(source, target, message)

	def save_speech(self, channel, user, message):
		if message[0] in ["!", ",", ";", "~", "#", ".", "§"]:
			return

		speechdb.connect()
		with speechdb.transaction():
			message = message.split()
			for i, word in enumerate(message):
				pprev_word = message[i-2] if i > 1 else None
				prev_word  = message[i-1] if i > 0 else None
				next_word  = message[i+1] if i < len(message)-1 else None
				nnext_word = message[i+2] if i < len(message)-2 else None

				pprev_cond = speechdb.none_or(Word.pprevious_word, pprev_word)
				prev_cond  = speechdb.none_or(Word.previous_word, prev_word)
				next_cond  = speechdb.none_or(Word.next_word, next_word)
				nnext_cond = speechdb.none_or(Word.nnext_word, nnext_word)

				word = Word.select().where((pprev_cond) & (prev_cond) & (next_cond) & (nnext_cond) & (Word.word == word)).first()
				if not word:
					word = Word.create(pprevious_word=pprev_word,
									   previous_word=prev_word,
									   next_word=next_word,
									   nnext_word=nnext_word,
									   word=message[i])
					word.save()
				Speech.create(word=word, user=user, chan=channel).save()
		speechdb.close()

if __name__ == '__main__':
	if os.environ.get('DEBUG'):
		import logging
		logger = logging.getLogger('peewee')
		logger.setLevel(logging.DEBUG)
		logger.addHandler(logging.StreamHandler())
	speechdb.connect()
	speechdb.create_tables()
	speechdb.close()
	client = CathoLingo(os.environ.get('USERNAME', 'CathoLingo'), realname=os.environ.get('REALNAME', 'la pizzeria'))
	client.connect(os.environ.get('IRC_HOST', 'chat.freenode.net'), int(os.environ.get('IRC_PORT', 6697)), tls=True, tls_verify=False)
	CommandListener(client).start()
	client.handle_forever()
