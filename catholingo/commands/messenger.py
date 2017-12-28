#!/usr/bin/python3
#coding: utf8

import datetime
import json
from commands import TalkativeCommandOrder, TextOrder, OrderPool

MESSENGER_PREFIX = "MESSENGER_"
MESSENGER_SEPARATOR = "_"

class MessengerOrder(TextOrder):
	def action(self, source, target, message):
		label = MESSENGER_SEPARATOR.join([MESSENGER_PREFIX, source, target])
		messages = json.loads(self.config(label, "[]"))
		for m in messages:
			self.client.message(source, target+": ["+m.get('datetime')+"] <"+m.get('author')+"> "+m.get('message'))
		if len(messages):
			self.set_config(label, "[]")

class TellCommand(TalkativeCommandOrder):
	COMMAND = "!tell"

	def talk(self, source, target, message):
		if len(message) < 2:
			return "Usage: "+self.COMMAND[0]+" nickname message..."
		label = MESSENGER_SEPARATOR.join([MESSENGER_PREFIX, source, message[0]])
		timestamp = '{0:%Y-%m-%d %H:%M:%S %Z}'.format(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)).replace('+00:00', '')

		messages = json.loads(self.config(label, "[]"))
		messages.append({'author': target, 'message': " ".join(message[1:]), 'datetime': timestamp})
		self.set_config(label, json.dumps(messages))
		return "OK"

if __name__ == '__main__':
	pool = OrderPool(orders=[MessengerOrder, TellCommand])
	pool.run()
