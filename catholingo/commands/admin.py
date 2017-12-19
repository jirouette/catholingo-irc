#!/usr/bin/python3
#coding: utf8

import database
import os
from commands import TalkativeCommandOrder, OrderPool

class SQLCommand(TalkativeCommandOrder):
	COMMAND = "!sql"

	def talk(self, source, target, message):
		with database.connection():
			payload = "Result = "
			results = database.execute(" ".join(message)).fetchall()
			if results:
				payload += " ".join([str(r) for r in results])
			return payload

class EvalCommand(TalkativeCommandOrder):
	COMMAND = "!eval"

	def talk(self, source, target, message):
		return eval(" ".join(message))

class ShellCommand(TalkativeCommandOrder):
	COMMAND = "!shell"

	def talk(self, source, target, message):
		return "\n".join(os.popen(" ".join(message)).read().split("\n")[:-1])

class MuteCommand(TalkativeCommandOrder):
	COMMAND = "!mute"

	def talk(self, source, target, message):
		self.client.mute(*message)
		print("muted",message)
		return "OK"

class ConfigCommand(TalkativeCommandOrder):
	COMMAND = "!config"

	def talk(self, source, target, message):
		if len(message) < 1:
			return "Usage: "+self.COMMAND[0]+" label [value]"
		elif len(message) == 1:
			return message[0] + "= " + str(self.config(message[0]))
		else:
			label = message[0]
			self.set_config(label, " ".join(message[1:]))
			return self.talk(source, target, [message[0]])

class UnmuteCommand(TalkativeCommandOrder):
	COMMAND = "!unmute"

	def talk(self, source, target, message):
		self.client.unmute(*message)
		print("unmuted",message)
		return "OK"

if __name__ == '__main__':
	orders = [MuteCommand, UnmuteCommand, ConfigCommand]
	if os.environ.get('UNSECURE_MODE') == '1':
		orders += [SQLCommand, EvalCommand, ShellCommand]
	pool = OrderPool(orders=orders)
	pool.run()
