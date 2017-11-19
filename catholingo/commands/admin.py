#!/usr/bin/python3
#coding: utf8

import speechdb
import time
import random
from commands import TalkativeCommandOrder, CommandOrderPool
from speechdb import Word, Speech

class SQLCommand(TalkativeCommandOrder):
	COMMAND = "!sql"

	def talk(self, source, target, message):
		speechdb.connect()
		payload = "Result = "
		results = speechdb.execute(" ".join(message)).fetchall()
		if results:
			payload += " ".join([str(r) for r in results])
		speechdb.close()
		return payload

class EvalCommand(TalkativeCommandOrder):
	COMMAND = "!eval"

	def talk(self, source, target, message):
		return eval(" ".join(message))

if __name__ == '__main__':
	pool = CommandOrderPool(commands=[SQLCommand, EvalCommand])
	pool.run()
