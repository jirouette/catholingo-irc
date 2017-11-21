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

if __name__ == '__main__':
	pool = OrderPool(orders=[SQLCommand, EvalCommand, ShellCommand])
	pool.run()
